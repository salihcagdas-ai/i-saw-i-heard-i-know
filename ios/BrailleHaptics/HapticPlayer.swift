import Combine
import CoreHaptics

@MainActor
final class HapticPlayer: ObservableObject {
    private var engine: CHHapticEngine?
    private var player: (any CHHapticPatternPlayer)?

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
            let next = try engine.makePlayer(with: pattern)
            try next.start(atTime: CHHapticTimeImmediate)
            player = next
        } catch {
            engine = nil
            throw error
        }
    }

    func stop() {
        try? player?.stop(atTime: CHHapticTimeImmediate)
        player = nil
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
