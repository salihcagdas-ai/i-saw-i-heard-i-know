import AVFoundation
import MediaPipeTasksVision
import OSLog

struct ASLPrediction {
    let letter: BrailleLetter
    let score: Float
}

final class ASLCamera: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    enum Event {
        case ready
        case guidance(String)
        case prediction(ASLPrediction)
        case failure(String)
    }

    let session = AVCaptureSession()

    // The session, recognizer, and frame history are managed on this queue.
    private let queue = DispatchQueue(label: "BrailleHaptics.camera", qos: .userInitiated)
    private let logger = Logger(subsystem: "local.salih.BrailleHaptics", category: "ASL")
    private var recognizer: GestureRecognizer?
    private var report: (@MainActor (Event) -> Void)?
    private var lastFrameTime: Int?
    private var lastGuidance: String?
    private var matchingLetter: BrailleLetter?
    private var matchingFrames = 0

    func start(report: @escaping @MainActor (Event) -> Void) {
        queue.async {
            self.stopCapture()
            self.report = report

            guard let model = Bundle.main.path(forResource: "gesture_recognizer_asl_0", ofType: "task") else {
                self.finish(.failure("ASL modeli bulunamadı. Modeli ekleyip uygulamayı yeniden derle."))
                return
            }
            do {
                let options = GestureRecognizerOptions()
                options.baseOptions.modelAssetPath = model
                options.runningMode = .video
                options.numHands = 2
                self.recognizer = try GestureRecognizer(options: options)
                try self.configureSession()
                self.session.startRunning()
                guard self.session.isRunning else { throw CameraError.unavailable }
                self.publish(.ready)
            } catch {
                self.logger.error("Camera or model initialization failed: \(error.localizedDescription, privacy: .public)")
                self.finish(.failure("Kamera veya ASL modeli başlatılamadı. Tekrar dene."))
            }
        }
    }

    func stop(completion: (@MainActor () -> Void)? = nil) {
        queue.async {
            self.stopCapture()
            if let completion {
                DispatchQueue.main.async { completion() }
            }
        }
    }

    private func configureSession() throws {
        guard session.inputs.isEmpty else { return }
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            throw CameraError.unavailable
        }
        let input = try AVCaptureDeviceInput(device: device)
        let output = AVCaptureVideoDataOutput()
        output.alwaysDiscardsLateVideoFrames = true
        output.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]

        session.beginConfiguration()
        defer { session.commitConfiguration() }
        if session.canSetSessionPreset(.vga640x480) {
            session.sessionPreset = .vga640x480
        }
        guard session.canAddInput(input) else { throw CameraError.unavailable }
        session.addInput(input)
        guard session.canAddOutput(output) else {
            session.removeInput(input)
            throw CameraError.unavailable
        }
        session.addOutput(output)
        output.setSampleBufferDelegate(self, queue: queue)
        if let connection = output.connection(with: .video) {
            if connection.isVideoRotationAngleSupported(90) {
                connection.videoRotationAngle = 90
            }
            if connection.isVideoMirroringSupported {
                connection.automaticallyAdjustsVideoMirroring = false
                connection.isVideoMirrored = false
            }
        }
    }

    func captureOutput(
        _ output: AVCaptureOutput,
        didOutput sampleBuffer: CMSampleBuffer,
        from connection: AVCaptureConnection
    ) {
        guard report != nil, let recognizer, let pixels = sampleBuffer.imageBuffer else { return }
        let seconds = sampleBuffer.presentationTimeStamp.seconds
        guard seconds.isFinite, seconds >= 0 else { return }
        let timestamp = Int(seconds * 1_000)
        if let lastFrameTime, timestamp - lastFrameTime < 100 { return }
        if let lastFrameTime, timestamp - lastFrameTime > 500 {
            matchingLetter = nil
            matchingFrames = 0
        }
        lastFrameTime = timestamp

        do {
            let image = try MPImage(pixelBuffer: pixels)
            let result = try recognizer.recognize(videoFrame: image, timestampInMilliseconds: timestamp)
            if result.landmarks.isEmpty {
                reject("Tek elini kadraja al.")
            } else if result.landmarks.count > 1 {
                reject("Kameraya yalnız bir el göster.")
            } else if let best = result.gestures.first?.max(by: { $0.score < $1.score }),
                      let label = best.categoryName?.uppercased(),
                      let letter = BrailleLetter(rawValue: label) {
                if best.score >= 0.75 {
                    accept(ASLPrediction(letter: letter, score: best.score))
                } else {
                    reject("Model skoru düşük. Elini sabit tut veya harfi elle seç.")
                }
            } else {
                reject("A, B veya C işaretini göster ya da harfi elle seç.")
            }
        } catch {
            logger.error("Gesture recognition failed: \(error.localizedDescription, privacy: .public)")
            finish(.failure("Görüntü işlenemedi. Tekrar dene."))
        }
    }

    private func accept(_ prediction: ASLPrediction) {
        if matchingLetter == prediction.letter {
            matchingFrames += 1
        } else {
            matchingLetter = prediction.letter
            matchingFrames = 1
        }
        if matchingFrames >= 3 {
            finish(.prediction(prediction))
        } else {
            guide("İşareti kısa süre sabit tut.")
        }
    }

    private func reject(_ instruction: String) {
        matchingLetter = nil
        matchingFrames = 0
        guide(instruction)
    }

    private func guide(_ instruction: String) {
        guard instruction != lastGuidance else { return }
        lastGuidance = instruction
        publish(.guidance(instruction))
    }

    private func publish(_ event: Event) {
        guard let report else { return }
        DispatchQueue.main.async { report(event) }
    }

    private func finish(_ event: Event) {
        guard let report else { return }
        self.report = nil
        // Let the sample-buffer callback return before stopping the capture session.
        queue.async {
            if self.report == nil {
                self.stopCapture()
            }
            DispatchQueue.main.async { report(event) }
        }
    }

    private func stopCapture() {
        report = nil
        if session.isRunning {
            session.stopRunning()
        }
        recognizer = nil
        lastFrameTime = nil
        lastGuidance = nil
        matchingLetter = nil
        matchingFrames = 0
    }

    private enum CameraError: Error {
        case unavailable
    }
}
