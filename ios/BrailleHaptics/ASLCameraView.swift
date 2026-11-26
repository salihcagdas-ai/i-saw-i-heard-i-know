import Accessibility
import AVFoundation
import Combine
import SwiftUI

@MainActor
struct ASLCameraView: View {
    @Environment(\.openURL) private var openURL
    @Environment(\.scenePhase) private var scenePhase
    @ObservedObject var haptics: HapticPlayer
    let speed: PlaybackSpeed

    @State private var camera = ASLCamera()
    @State private var stage = Stage.idle
    @State private var scanID: UUID?
    @State private var guidance = ""
    @State private var draft: BrailleLetter?
    @State private var playbackFailed = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                switch stage {
                case .idle:
                    Text("Ön kameraya A, B veya C işaretini tek elle göster.")
                    scanButton("Taramayı başlat")
                case .preparing:
                    ProgressView("Kamera hazırlanıyor")
                    Button("İptal") {
                        stopScan()
                        stage = .idle
                    }
                case .scanning:
                    CameraPreview(session: camera.session)
                        .aspectRatio(3.0 / 4, contentMode: .fit)
                        .frame(maxWidth: 360)
                        .clipShape(.rect(cornerRadius: 12))
                        .accessibilityHidden(true)
                    Text(guidance)
                    scanButton("Yeniden tara")
                    Button("Elle harf seç") { review(nil) }
                case .review(let prediction):
                    if let prediction {
                        Text("Tahmin: \(prediction.letter.rawValue)")
                            .font(.title2.bold())
                        Text("Model skoru \(prediction.score.formatted(.percent.precision(.fractionLength(0))))")
                    }
                    Picker("Onaylanacak harf", selection: $draft) {
                        Text("Harf seç").tag(nil as BrailleLetter?)
                        ForEach(BrailleLetter.allCases) { letter in
                            Text(letter.rawValue).tag(Optional(letter))
                        }
                    }
                    .pickerStyle(.segmented)
                    Button("Onayla ve titreştir", action: confirm)
                        .buttonStyle(.borderedProminent)
                        .disabled(draft == nil || haptics.isPlaying)
                    scanButton("Yeniden tara")
                case .confirmed(let letter):
                    Text(haptics.isPlaying
                         ? "\(letter.rawValue) titreşimi oynatılıyor."
                         : "Onaylanan harf \(letter.rawValue).")
                        .font(.headline)
                    scanButton("Yeni işaret tara")
                case .permissionDenied:
                    Text("Kamerayı kullanmak için Ayarlar’dan kamera izni ver.")
                    Button("Ayarları aç") {
                        if let url = URL(string: UIApplication.openSettingsURLString) {
                            openURL(url)
                        }
                    }
                    scanButton("Yeniden dene")
                    Button("Elle harf seç") { review(nil) }
                case .failed(let message):
                    Text(message)
                    scanButton("Yeniden dene")
                    Button("Elle harf seç") { review(nil) }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(20)
        }
        .navigationTitle("Kameradan tanı")
        .onAppear { haptics.stop() }
        .onDisappear {
            stopScan()
            haptics.stop()
        }
        .onChange(of: scenePhase) { _, phase in
            if phase != .active { haptics.stop() }
            if phase == .background, scanID != nil {
                stopScan()
                stage = .idle
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: AVCaptureSession.wasInterruptedNotification,
                                                        object: camera.session)
            .receive(on: DispatchQueue.main)) { _ in
            failScan("Kamera kesintiye uğradı. Yeniden dene.")
        }
        .onReceive(NotificationCenter.default.publisher(for: AVCaptureSession.runtimeErrorNotification,
                                                        object: camera.session)
            .receive(on: DispatchQueue.main)) { _ in
            failScan("Kamera çalıştırılamadı. Yeniden dene.")
        }
        .alert("Titreşim oynatılamadı", isPresented: $playbackFailed) {
            Button("Tamam", role: .cancel) {}
        } message: {
            Text("Titreşim ayarını kontrol edip yeniden onayla.")
        }
    }

    private func scanButton(_ title: String) -> some View {
        Button(title, action: startScan)
            .buttonStyle(.bordered)
            .disabled(haptics.isPlaying)
    }

    private func startScan() {
        guard !haptics.isPlaying else { return }
        stopScan()
        draft = nil
        guidance = "Tek elini kadraja al."
        stage = .preparing
        let request = UUID()
        scanID = request

        Task { @MainActor in
            let granted = await AVCaptureDevice.requestAccess(for: .video)
            guard scanID == request else { return }
            guard granted else {
                stopScan()
                stage = .permissionDenied
                return
            }
            camera.start { event in
                guard scanID == request else { return }
                switch event {
                case .ready:
                    stage = .scanning
                case .guidance(let instruction):
                    guidance = instruction
                case .prediction(let prediction):
                    review(prediction)
                case .failure(let message):
                    failScan(message)
                }
            }
        }
    }

    private func stopScan() {
        scanID = nil
        camera.stop()
    }

    private func failScan(_ message: String) {
        guard scanID != nil else { return }
        stopScan()
        stage = .failed(message)
    }

    private func review(_ prediction: ASLPrediction?) {
        let request = UUID()
        scanID = request
        camera.stop {
            guard scanID == request else { return }
            scanID = nil
            draft = prediction?.letter
            stage = .review(prediction)
            if let prediction {
                AccessibilityNotification.Announcement("Tahmin \(prediction.letter.rawValue). Harfi onayla veya değiştir.").post()
            }
        }
    }

    private func confirm() {
        guard case .review = stage, let draft, !haptics.isPlaying else { return }
        do {
            try haptics.play(draft, at: speed)
            stage = .confirmed(draft)
        } catch {
            playbackFailed = true
        }
    }

    private enum Stage {
        case idle, preparing, scanning
        case review(ASLPrediction?)
        case confirmed(BrailleLetter)
        case permissionDenied
        case failed(String)
    }
}

private struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.previewLayer.videoGravity = .resizeAspectFill
        view.previewLayer.session = session
        return view
    }

    func updateUIView(_ view: PreviewView, context: Context) {}

    final class PreviewView: UIView {
        override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
        var previewLayer: AVCaptureVideoPreviewLayer { layer as! AVCaptureVideoPreviewLayer }

        override func layoutSubviews() {
            super.layoutSubviews()
            guard let connection = previewLayer.connection else { return }
            if connection.isVideoRotationAngleSupported(90) {
                connection.videoRotationAngle = 90
            }
            if connection.isVideoMirroringSupported {
                connection.automaticallyAdjustsVideoMirroring = false
                connection.isVideoMirrored = true
            }
        }
    }
}
