enum BrailleLetter: String, CaseIterable, Identifiable {
    case a = "A"
    case b = "B"
    case c = "C"

    var id: String { rawValue }

    private var raisedDots: Set<Int> {
        switch self {
        case .a: [1]
        case .b: [1, 2]
        case .c: [1, 4]
        }
    }

    func pulses(at speed: PlaybackSpeed) -> [HapticPulse] {
        // Two short, closely spaced pulses mark the start of a cell.
        let marker = [
            HapticPulse(start: 0, duration: 0.055),
            HapticPulse(start: 0.13, duration: 0.055),
        ]
        let slots = (1...6).map { dot in
            HapticPulse(
                start: 0.43 + Double(dot - 1) * 0.36 * speed.scale,
                duration: (raisedDots.contains(dot) ? 0.22 : 0.075) * speed.scale
            )
        }
        return marker + slots
    }
}

enum PlaybackSpeed: String, CaseIterable, Identifiable {
    case slow = "Yavaş"
    case normal = "Normal"
    case fast = "Hızlı"

    var id: String { rawValue }

    var scale: Double {
        switch self {
        case .slow: 1.30
        case .normal: 1.0
        case .fast: 0.82
        }
    }
}

struct HapticPulse {
    let start: Double
    let duration: Double
}
