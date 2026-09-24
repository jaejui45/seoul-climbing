import SwiftUI

struct FilterBar: View {
    @Binding var filter: GymStore.Filter

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(GymStore.Filter.allCases) { f in
                    Button {
                        filter = f
                    } label: {
                        Text(f.rawValue)
                            .font(.subheadline.weight(.medium))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 7)
                            .background(filter == f ? Color.orange : Color(.secondarySystemBackground), in: Capsule())
                            .foregroundStyle(filter == f ? .white : .primary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)
        }
    }
}
