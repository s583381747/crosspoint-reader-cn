#include "Lyra3CoversTheme.h"

#include <GfxRenderer.h>
#include <HalStorage.h>

#include <cstdint>
#include <string>
#include <vector>

#include "RecentBooksStore.h"
#include "components/UITheme.h"
#include "components/icons/cover.h"
#include "fontIds.h"

// Internal constants
namespace {
constexpr int hPaddingInSelection = 8;
constexpr int cornerRadius = 6;
}  // namespace

void Lyra3CoversTheme::drawRecentBookCover(GfxRenderer& renderer, Rect rect, const std::vector<RecentBook>& recentBooks,
                                           const int selectorIndex, bool& coverRendered, bool& coverBufferStored,
                                           bool& bufferRestored, std::function<bool()> storeCoverBuffer) const {
  const bool hasContinueReading = !recentBooks.empty();

  if (hasContinueReading) {
    const int contentX = Lyra3CoversMetrics::values.contentSidePadding;
    const int contentWidth = rect.width - 2 * contentX;
    const int titleLineHeight = renderer.getLineHeight(UI_12_FONT_ID);
    const int authorLineHeight = renderer.getLineHeight(SMALL_FONT_ID);
    const int itemHeight = titleLineHeight + authorLineHeight + 8;
    const int maxBooks = std::min(static_cast<int>(recentBooks.size()), 3);

    int currentY = rect.y + 4;

    for (int i = 0; i < maxBooks; i++) {
      bool bookSelected = (selectorIndex == i);

      if (bookSelected) {
        renderer.fillRoundedRect(contentX - 4, currentY - 2, contentWidth + 8, itemHeight, cornerRadius,
                                 true, true, true, true, Color::LightGray);
      }

      // Title
      auto truncTitle = renderer.truncatedText(UI_12_FONT_ID, recentBooks[i].title.c_str(), contentWidth,
                                               EpdFontFamily::REGULAR);
      renderer.drawText(UI_12_FONT_ID, contentX, currentY, truncTitle.c_str(), true, EpdFontFamily::REGULAR);

      // Author
      if (!recentBooks[i].author.empty()) {
        auto truncAuthor = renderer.truncatedText(SMALL_FONT_ID, recentBooks[i].author.c_str(), contentWidth,
                                                  EpdFontFamily::REGULAR);
        renderer.drawText(SMALL_FONT_ID, contentX, currentY + titleLineHeight + 2, truncAuthor.c_str(), true,
                          EpdFontFamily::REGULAR);
      }

      currentY += itemHeight;
    }

    coverRendered = true;
    coverBufferStored = true;
  } else {
    drawEmptyRecents(renderer, rect);
  }
}
