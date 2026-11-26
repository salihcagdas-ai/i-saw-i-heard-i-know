import Combine
import CoreHaptics
import Foundation

@MainActor
final class HapticPlayer: ObservableObject {
    @Published private(set) var isPlaying = false

    private var engine: CHHapticEngine?
    private var player: (any CHHapticAdvancedPatternPlayer)?
    private var playbackID: UUID?

    var isSupported: Bool {
        CHHapticEngine.capabilitiesForHardware().supportsHaptics
    }

    func play(_ letter: BrailleLetter, at speed: PlaybackSpeed) throws {
        stop()

        let events = letter.pulses(at: speed).map { pulse in
            CHHapticEvent(
                eventType: .hapticContinuous,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 1),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.75),
                ],
                relativeTime: pulse.start,
                duration: pulse.duration
            )
        }

        do {
            let engine = try runningEngine()
            let pattern = try CHHapticPattern(events: events, parameters: [])
            let next = try engine.makeAdvancedPlayer(with: pattern)
            let id = UUID()
            let finish: @Sendable () -> Void = { [weak self] in
                Task { @MainActor [weak self] in
                    guard let self, self.playbackID == id else { return }
                    self.clearPlayback()
                }
            }
            engine.resetHandler = finish
            engine.stoppedHandler = { _ in finish() }
            next.completionHandler = { _ in finish() }
            try next.start(atTime: CHHapticTimeImmediate)
            player = next
            playbackID = id
            isPlaying = true
        } catch {
            engine = nil
            throw error
        }
    }

    func stop() {
        let current = player
        clearPlayback()
        try? current?.stop(atTime: CHHapticTimeImmediate)
    }

    private func clearPlayback() {
        player = nil
        playbackID = nil
        isPlaying = false
    }

    private func runningEngine() throws -> CHHapticEngine {
        if let engine {
            try engine.start()
            return engine
        }

        let newEngine = try CHHapticEngine()
        newEngine.playsHapticsOnly = true
        newEngine.isAutoShutdownEnabled = true
        try newEngine.start()
        engine = newEngine
        return newEngine
    }
}
