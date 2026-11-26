import Accessibility
import SwiftUI

@main
struct BrailleHapticsApp: App {
    var body: some Scene {
        WindowGroup {
            BraillePracticeView()
        }
    }
}

@MainActor
struct BraillePracticeView: View {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var haptics = HapticPlayer()
    @State private var speed = PlaybackSpeed.normal
    @State private var lastLetter: BrailleLetter?
    @State private var hiddenLetter: BrailleLetter?
    @State private var feedback = ""
    @State private var playbackFailed = false

    var body: some View {
        NavigationStack {
            if haptics.isSupported {
                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        Text(hiddenLetter == nil
                             ? "Titreşimini öğrenmek için bir harf seç."
                             : "Hangi harfi hissettin?")
                            .font(.title3)

                        NavigationLink {
                            ASLCameraView(haptics: haptics, speed: speed)
                        } label: {
                            Label("Kameradan tanı", systemImage: "camera")
                        }
                        .buttonStyle(.bordered)

                        HStack(spacing: 12) {
                            ForEach(BrailleLetter.allCases) { letter in
                                Button {
                                    select(letter)
                                } label: {
                                    Text(letter.rawValue)
                                        .font(.title2.weight(.semibold))
                                        .frame(maxWidth: .infinity, minHeight: 52)
                                }
                                .buttonStyle(.borderedProminent)
                                .accessibilityHint(hiddenLetter == nil
                                                   ? "Harf titreşimini oynatır"
                                                   : "Bu harfi yanıt olarak seçer")
                            }
                        }

                        Picker("Titreşim hızı", selection: $speed) {
                            ForEach(PlaybackSpeed.allCases) { value in
                                Text(value.rawValue).tag(value)
                            }
                        }

                        Button("Gizli harf oynat", action: playHiddenLetter)
                            .buttonStyle(.bordered)

                        ViewThatFits(in: .horizontal) {
                            HStack { playbackControls }
                            VStack(alignment: .leading) { playbackControls }
                        }

                        if !feedback.isEmpty {
                            Text(feedback)
                                .font(.headline)
                        }
                    }
                    .padding(20)
                }
                .navigationTitle("Titreşimli Braille")
            } else {
                ContentUnavailableView(
                    "Titreşim desteği gerekli",
                    systemImage: "waveform",
                    description: Text("Bu denemeyi titreşim destekleyen bir iPhone’da aç.")
                )
            }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase != .active {
                haptics.stop()
            }
        }
        .alert("Titreşim oynatılamadı", isPresented: $playbackFailed) {
            Button("Tamam", role: .cancel) {}
        } message: {
            Text("Titreşim ayarını kontrol edip tekrar dene.")
        }
    }

    @ViewBuilder
    private var playbackControls: some View {
        Button("Tekrar oynat") {
            if let lastLetter {
                _ = play(lastLetter)
            }
        }
        .disabled(lastLetter == nil)

        Button("Durdur") {
            haptics.stop()
        }
        .disabled(lastLetter == nil)
    }

    private func select(_ letter: BrailleLetter) {
        if let hiddenLetter {
            haptics.stop()
            self.hiddenLetter = nil
            feedback = letter == hiddenLetter
                ? "Doğru. Harf \(hiddenLetter.rawValue)."
                : "Harf \(hiddenLetter.rawValue)."
            AccessibilityNotification.Announcement(feedback).post()
        } else if play(letter) {
            feedback = "Son örnek \(letter.rawValue)"
        }
    }

    private func playHiddenLetter() {
        guard let letter = BrailleLetter.allCases.randomElement(), play(letter) else { return }
        hiddenLetter = letter
        feedback = ""
    }

    private func play(_ letter: BrailleLetter) -> Bool {
        do {
            try haptics.play(letter, at: speed)
            lastLetter = letter
            return true
        } catch {
            playbackFailed = true
            return false
        }
    }
}
