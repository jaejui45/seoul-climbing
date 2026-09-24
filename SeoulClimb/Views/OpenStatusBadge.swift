import SwiftUI

struct OpenStatusBadge: View {
    let status: OpenStatus

    var body: some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(color.opacity(0.15), in: Capsule())
            .foregroundStyle(color)
    }

    private var text: String {
        switch status {
        case .open(let closesAt): "영업중 · \(closesAt) 종료"
        case .opensLater(let opensAt): "영업 전 · \(opensAt) 오픈"
        case .closedToday: "영업 종료"
        case .unknown: "시간 정보 없음"
        }
    }

    private var color: Color {
        switch status {
        case .open: .green
        case .opensLater: .orange
        case .closedToday: .red
        case .unknown: .gray
        }
    }
}
