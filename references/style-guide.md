# WeChat Article Visual Style

Use this style when the user asks for the default `wechat-writer` look or references the screenshots in this skill folder.

## Overall Impression

Create a clean, analytical, product-review editorial style. The article should feel like a thoughtful long-form WeChat analysis: mostly white space and readable text, punctuated by strong comparison modules, muted colored callouts, and simple data-like cards.

## Layout

- Use a white article canvas with generous side padding.
- Keep the body width close to WeChat's natural article width: about 677px.
- Use large vertical rhythm: paragraphs should breathe, modules should sit apart.
- Avoid decorative clutter. Let charts, cards, and callouts carry visual interest.
- Prefer full-width modules inside the article column, not tiny floating badges.
- Use rounded rectangles sparingly for comparison cards, placeholders, and callouts. Keep radius around 8-14px.

## Typography

- Use system Chinese UI fonts.
- Body text should be dark, confident, and readable: 16-18px with 1.75-1.9 line height.
- Headings should be bold and compact, not poster-like.
- Use bullet-dot section headings for H2/H3 when suitable: colored dot on the left, bold black title.
- Preserve a direct, analytical tone in visible text.

## Palette

Use a restrained palette derived from the references:

- Ink: `#1F1F1F` for main text.
- Muted gray: `#6F6F68` for captions and helper copy.
- Border gray: `#DDDCD5` for separators and card borders.
- Purple: `#6253C9` for consumer/toC/creative-side emphasis.
- Green: `#5B8F22` for business/toB/productivity-side emphasis.
- Amber: `#9A5B08` for cost, warning, or reality-check emphasis.
- Lavender background: `#EFEDFF`.
- Green background: `#EDF6E4`.
- Amber background: `#FFF2DC`.
- Warm neutral panel: `#F5F4EE`.

Do not make the whole article one color. Use black text and white space as the base; colors should label meaning.

## Components

### Comparison Hero

For articles comparing two products, ideas, approaches, or people, create a dark comparison block near the top when useful:

- Dark purple-black background.
- Two columns separated by a vertical divider.
- Large numeric or keyword emphasis in purple on the left and green on the right.
- Pill labels and small tags.
- A centered `VS` marker.

### Callouts

Use callouts for thesis statements, reality checks, and important takeaways:

- Left border in the semantic accent color.
- Soft background matching the accent.
- Text color should be a darker version of the accent.
- Use amber for constraints/costs/risks.
- Use green for opportunity/productivity/business value.
- Use purple for user experience, creative, or consumer-side observations.

### Cards

Use bordered white cards for structured comparison facts:

- Two-column cards are preferred for product comparisons.
- Keep labels on the left and values aligned right.
- Use small colored highlight spans for key values.
- Use red text only for negative status or risks; keep it rare.

### Placeholder/Image Modules

When the article needs an image slot but no image is available, render a warm neutral placeholder:

- Light warm background.
- Dashed border.
- Centered small icon-like symbol if easy.
- Short title and one helper line.

### Code Blocks

Render code as a warm neutral block, not a dark terminal:

- Warm paper background.
- Thin neutral border.
- Rounded corners.
- Monospace text.

## Cover Direction

For generated covers, prefer an editorial/product-analysis visual:

- Landscape 2.35:1.
- Clean white or very dark background depending on the topic.
- One strong central comparison or product metaphor.
- Purple-vs-green semantic contrast when comparing two sides.
- Minimal shapes, clean cards, thin dividers, high negative space.
- No embedded text unless the user explicitly requests it.

## Avoid

- Marketing landing-page gradients.
- Dense decorative backgrounds.
- Cartoonish illustration unless the article topic explicitly calls for it.
- Overly soft pastel-only layouts.
- Long blocks of tiny text in images.
