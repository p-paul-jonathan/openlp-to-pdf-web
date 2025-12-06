import os
import json
import textwrap
from weasyprint import HTML, CSS

PT_TO_PX = 1  # OpenLP visual match


# --------------------------------------------------------
# THEME LOADING
# --------------------------------------------------------

def find_theme_json_and_root(theme_extract_dir):
    for root, dirs, files in os.walk(theme_extract_dir):
        for f in files:
            if f.endswith(".json"):
                return os.path.join(root, f), root
    raise FileNotFoundError("Theme JSON not found inside theme directory")


def load_theme(theme_extract_dir):
    theme_path, theme_root = find_theme_json_and_root(theme_extract_dir)
    with open(theme_path, "r", encoding="utf-8") as f:
        return json.load(f), theme_root


# --------------------------------------------------------
# BACKGROUND (image allowed)
# --------------------------------------------------------

def build_background_css(theme, theme_dir):
    bg_type = theme.get("background_type", "solid")

    if bg_type == "solid":
        return f"background: {theme.get('background_color', '#000')};"

    if bg_type == "gradient":
        start = theme.get("background_start_color", "#000")
        end = theme.get("background_end_color", "#000")
        direction = theme.get("background_direction", "vertical")
        css_dir = "to bottom" if direction == "vertical" else "to right"
        return f"background: linear-gradient({css_dir}, {start}, {end});"

    if bg_type == "image":
        # Locate background image
        bg = theme.get("background_filename")
        filename = None

        if isinstance(bg, dict) and "parts" in bg:
            filename = bg["parts"][-1]
        elif isinstance(bg, str):
            filename = bg

        if filename:
            image_path = os.path.join(theme_dir, filename)
            image_path = os.path.abspath(image_path).replace("\\", "/")

            if os.path.exists(image_path):
                return f"""
                    background-image: url("file://{image_path}");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                """

        # fallback if missing
        return f"background: {theme.get('background_color', '#000')};"

    return "background: #000;"


# --------------------------------------------------------
# STYLE
# --------------------------------------------------------

def build_page_style(theme, theme_dir):
    width = int(theme["font_main_width"])
    height = int(theme["font_main_height"])
    font = theme["font_main_name"]
    font_pt = float(theme["font_main_size"])
    font_px = font_pt * PT_TO_PX
    color = theme["font_main_color"]

    h_align = theme.get("display_horizontal_align", 2)
    v_align = theme.get("display_vertical_align", 1)
    align_map = {0: "left", 1: "right", 2: "center", 3: "justify"}
    v_map = {0: "flex-start", 1: "center", 2: "flex-end"}

    # line height
    line_adjust = float(theme.get("font_main_line_adjustment", 1.0)) or 1.0
    if line_adjust <= 0:
        line_adjust = 1.0

    bg_css = build_background_css(theme, theme_dir)

    css = f"""
    @page {{
        size: {width}px {height}px;
        margin: 0;
    }}

    body {{
        margin: 0;
        font-family: "{font}", sans-serif;
    }}

    .page {{
        width: {width}px;
        height: {height}px;
        display: flex;
        justify-content: {align_map.get(h_align)};
        align-items: {v_map.get(v_align)};
        padding: 60px;
        box-sizing: border-box;
        page-break-after: always;
        {bg_css}
    }}

    .content {{
        font-size: {font_px}px;
        color: {color};
        white-space: pre-line;
        text-align: {align_map.get(h_align)};
        line-height: {line_adjust};
        width: 100%;
    }}

    .page:last-child {{
        page-break-after: auto;
    }}
    """

    return width, height, css


# --------------------------------------------------------
# PAGINATION + WRAPPING
# --------------------------------------------------------

def estimate_lines_per_page(theme):
    region_height = float(theme["font_main_height"])
    font_px = float(theme["font_main_size"]) * PT_TO_PX

    raw_adj = theme.get("font_main_line_adjustment", 1.0)
    try:
        line_adj = float(raw_adj)
    except:
        line_adj = 1.0
    if line_adj <= 0:
        line_adj = 1.0

    line_height = font_px * line_adj
    max_lines = int(region_height / line_height)
    return max(max_lines, 3)


def wrap_slide_text(slide_text, theme):
    width_px = float(theme["font_main_width"])
    font_px = float(theme["font_main_size"]) * PT_TO_PX
    approx_char_width = font_px * 0.60
    max_chars = max(10, int(width_px / approx_char_width))

    wrapper = textwrap.TextWrapper(
        width=max_chars,
        drop_whitespace=False,
        replace_whitespace=False,
    )

    lines = []
    for raw in slide_text.splitlines():
        if not raw.strip():
            lines.append("")
        else:
            lines.extend(wrapper.wrap(raw))

    return lines


def split_slide_to_pages(slide_text, theme):
    max_lines = estimate_lines_per_page(theme)
    wrapped = wrap_slide_text(slide_text, theme)

    pages = []
    for i in range(0, len(wrapped), max_lines):
        chunk = wrapped[i:i + max_lines]
        pages.append("<br>".join(chunk))
    return pages


# --------------------------------------------------------
# HTML COMPOSITION
# --------------------------------------------------------

def build_pages(slides, theme):
    all_pages = []
    for slide in slides:
        for page in split_slide_to_pages(slide, theme):
            all_pages.append(f"""
                <div class="page">
                    <div class="content">{page}</div>
                </div>
            """)
    return all_pages


def compose_document(pages, css):
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>{css}</style>
    </head>
    <body>
        {"".join(pages)}
    </body>
    </html>
    """
    return html


# --------------------------------------------------------
# WEASYPRINT PDF RENDERING
# --------------------------------------------------------

def convert_slides_to_pdf(slides, theme_extract_dir, job_dir):
    if not os.path.exists(job_dir):
        raise FileNotFoundError("Job directory missing")

    theme, theme_root = load_theme(theme_extract_dir)
    width, height, css = build_page_style(theme, theme_root)

    pages = build_pages(slides, theme)
    html = compose_document(pages, css)

    pdf_path = os.path.join(job_dir, "slides.pdf")

    HTML(string=html, base_url=theme_root).write_pdf(pdf_path)

    if not os.path.exists(pdf_path):
        raise RuntimeError("WeasyPrint failed to generate PDF")

    return pdf_path
