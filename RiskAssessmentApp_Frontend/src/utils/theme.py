from dataclasses import dataclass
import flet as ft


@dataclass
class ThemeColors:
    # Core tokens
    bg: str
    surface: str
    card_bg: str
    border: str
    text_primary: str
    text_secondary: str
    primary: str
    primary_seed: str
    success: str
    warning: str
    danger: str
    # Navigation
    sidebar_bg: str
    sidebar_item: str
    sidebar_item_active: str
    sidebar_text: str
    muted: str
    # Modern 2025 additions
    accent: str
    gradient_start: str
    gradient_end: str
    shadow: str
    hover_bg: str
    button_primary: str
    button_secondary: str
    button_text: str
    glass_bg: str


def get_theme_colors(mode: ft.ThemeMode) -> ThemeColors:
    is_dark = mode == ft.ThemeMode.DARK

    if is_dark:
        return ThemeColors(
            bg="#0A0E1A",  # Deep space blue
            surface="#131829",  # Dark navy
            card_bg="#1E293B",  # Card background
            border="#334155",  # Border color
            text_primary="#F8FAFC",  # Pure white
            text_secondary="#94A3B8",  # Slate gray
            primary="#3B82F6",  # Modern blue
            primary_seed="#3B82F6",
            success="#10B981",  # Emerald
            warning="#F59E0B",  # Amber
            danger="#EF4444",  # Red
            sidebar_bg="#0F172A",  # Darker navy
            sidebar_item="#1E293B",  # Slate 800
            sidebar_item_active="#3B82F6",  # Primary blue
            sidebar_text="#F1F5F9",  # Light slate
            muted="#64748B",
            accent="#8B5CF6",  # Purple
            gradient_start="#1E293B",  # Gradient start
            gradient_end="#0F172A",  # Gradient end
            shadow="#00000040",  # Shadow with opacity
            hover_bg="#334155",  # Hover background
            button_primary="#3B82F6",  # Primary button
            button_secondary="#475569",  # Secondary button
            button_text="#FFFFFF",  # Button text
            glass_bg="#1E293B80"  # Glass effect
        )
    else:
        return ThemeColors(
            bg="#F8FAFC",  # Light slate
            surface="#FFFFFF",  # Pure white
            card_bg="#FFFFFF",  # Card background
            border="#E2E8F0",  # Border color
            text_primary="#0F172A",  # Dark slate
            text_secondary="#64748B",  # Slate 500
            primary="#3B82F6",  # Modern blue
            primary_seed="#3B82F6",
            success="#10B981",  # Emerald
            warning="#F59E0B",  # Amber
            danger="#EF4444",  # Red
            sidebar_bg="#1E293B",  # Dark sidebar
            sidebar_item="#334155",  # Slate 700
            sidebar_item_active="#3B82F6",  # Primary blue
            sidebar_text="#F1F5F9",  # Light text
            muted="#9CA3AF",
            accent="#8B5CF6",  # Purple
            gradient_start="#F1F5F9",  # Light gradient
            gradient_end="#E2E8F0",  # Slate 200
            shadow="#0F172A20",  # Light shadow
            hover_bg="#F1F5F9",  # Hover background
            button_primary="#3B82F6",  # Primary button
            button_secondary="#E5E7EB",  # Secondary button
            button_text="#FFFFFF",  # Button text
            glass_bg="#FFFFFF90"  # Glass effect
        )


# ---------- Apple-like gradient helpers (using existing palette colors) ----------
def _clamp_channel(v: int) -> int:
    return max(0, min(255, v))


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{_clamp_channel(r):02X}{_clamp_channel(g):02X}{_clamp_channel(b):02X}"


def _adjust_hex(h: str, factor: float) -> str:
    """Adjust hex brightness: factor > 0 lightens, < 0 darkens."""
    r, g, b = _hex_to_rgb(h)
    if factor >= 0:
        r = r + (255 - r) * factor
        g = g + (255 - g) * factor
        b = b + (255 - b) * factor
    else:
        f = 1 + factor
        r = r * f
        g = g * f
        b = b * f
    return _rgb_to_hex(int(r), int(g), int(b))


def build_gradient(base_hex: str) -> ft.LinearGradient:
    """Create an Apple-like subtle 3-stop gradient from a base color."""
    dark = _adjust_hex(base_hex, -0.45)
    mid = base_hex
    light = _adjust_hex(base_hex, 0.25)
    return ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[dark, mid, light],
    )


def darken_color(base_hex: str, amount: float = 0.25) -> str:
    """Public helper to darken a hex color by amount (0..1)."""
    return _adjust_hex(base_hex, -abs(amount))


# ---------- Theming normalizer for legacy hard-coded colors ----------
_TEXT_PRIMARY_HEX = {"#2c3e50", "#2C3E50"}
_TEXT_SECONDARY_HEX = {"#7f8c8d", "#666666", "#95a5a6"}
_SURFACE_HEX = {
    "white", "#ffffff", "#FFFFFF",
    "#f5f7fa", "#f8f9fa", "#f5f5f5", "#f9f9f9", "#f0f2f5",
    "#e3f2fd", "#ffebee"
}
_BORDER_HEX = {"#e6e9ed", "#EEEEEE"}

_ACCENT_MAP = {
    "#3498db": "primary",  # Blue
    "#e74c3c": "danger",   # Red
    "#2ecc71": "success",  # Green
    "#f39c12": "warning",  # Orange
    "#95a5a6": "muted",    # Gray
}

# Case-insensitive helpers
_TEXT_PRIMARY_HEX_L = {c.lower() for c in _TEXT_PRIMARY_HEX}
_TEXT_SECONDARY_HEX_L = {c.lower() for c in _TEXT_SECONDARY_HEX}
_SURFACE_HEX_L = {c.lower() for c in _SURFACE_HEX}
_BORDER_HEX_L = {c.lower() for c in _BORDER_HEX}
_ACCENT_MAP_L = {k.lower(): v for k, v in _ACCENT_MAP.items()}

def _build_default_dark_set():
    vals = []
    for name in [
        "BLACK", "BLACK87", "BLACK54", "BLACK45", "BLACK26", "BLACK12",
        "GREY_900", "GREY_800", "GREY_700"
    ]:
        v = getattr(ft.Colors, name, None)
        if v is not None:
            vals.append(v)
    return set(vals)

_DEFAULT_DARK_COLORS = _build_default_dark_set()


def apply_theme_to_control(control: ft.Control, colors: ThemeColors) -> None:
    """Recursively normalize control colors to current theme.
    This fixes dark/light mode for legacy views without touching every line.
    """
    try:
        # Text color
        if isinstance(control, ft.Text):
            current = getattr(control, "color", None)
            # Default text color when unset or black-ish
            current_l = str(current).lower() if current else None
            if (not current
                or current in _DEFAULT_DARK_COLORS
                or current_l in {"#000000", "black"}):
                control.color = colors.text_primary
            elif current_l in _TEXT_PRIMARY_HEX_L:
                control.color = colors.text_primary
            elif current_l in _TEXT_SECONDARY_HEX_L:
                control.color = colors.text_secondary
            elif current_l in _ACCENT_MAP_L:
                key = _ACCENT_MAP_L[current_l]
                control.color = getattr(colors, key, colors.text_primary)

        # Container backgrounds / borders
        if isinstance(control, ft.Container):
            # Preserve existing gradients (e.g., Apple-themed sidebar) – do not override
            if getattr(control, "gradient", None) is None:
                bg = getattr(control, "bgcolor", None)
                bg_l = str(bg).lower() if bg is not None else None
                if bg is None or bg_l in {"white", "#ffffff"} or (bg_l in _SURFACE_HEX_L):
                    control.bgcolor = colors.surface
                if bg_l in _ACCENT_MAP_L:
                    key = _ACCENT_MAP_L[bg_l]
                    control.bgcolor = getattr(colors, key, colors.surface)
            if getattr(control, "border", None) and hasattr(control.border, "top"):
                # Best-effort border color normalization for any side
                try:
                    b = control.border
                    sides = [getattr(b, s) for s in ("top", "right", "bottom", "left")]
                    if any(getattr(s, "color", None) and str(getattr(s, "color")).lower() in _BORDER_HEX_L for s in sides if s is not None):
                        control.border = ft.border.all(1, colors.border)
                except Exception:
                    pass

        # ElevatedButton normalization
        if isinstance(control, ft.ElevatedButton):
            bg = getattr(control, "bgcolor", None)
            if bg in _ACCENT_MAP:
                key = _ACCENT_MAP[bg]
                control.bgcolor = getattr(colors, key, colors.button_primary)
                control.color = colors.button_text
            if not bg:
                control.bgcolor = colors.button_secondary
                if hasattr(control, "color") and not getattr(control, "color", None):
                    control.color = colors.text_primary

        # Icon normalization
        if isinstance(control, ft.Icon):
            ico = getattr(control, "color", None)
            ico_l = str(ico).lower() if ico else None
            if not ico or ico in _DEFAULT_DARK_COLORS or ico_l in {"#000000", "black"}:
                control.color = colors.text_secondary
            elif ico_l in _TEXT_PRIMARY_HEX_L:
                control.color = colors.text_primary
            elif ico_l in _TEXT_SECONDARY_HEX_L:
                control.color = colors.text_secondary
            elif ico_l in _ACCENT_MAP_L:
                key = _ACCENT_MAP_L[ico_l]
                control.color = getattr(colors, key, colors.text_secondary)

        # Divider
        if isinstance(control, ft.Divider):
            if str(getattr(control, "color", None)).lower() in _BORDER_HEX_L:
                control.color = colors.border

        # DataTable normalization (header/background border colors)
        if isinstance(control, ft.DataTable):
            try:
                hdr = getattr(control, "heading_row_color", None)
                if hdr in _SURFACE_HEX or hdr in {"#f8f9fa", "#F8F9FA"}:
                    control.heading_row_color = colors.surface
                # Best-effort border color swap
                if getattr(control, "border", None):
                    # Some Flet versions use ft.BorderSide; we replace with theme border
                    control.border = ft.border.all(1, colors.border)
            except Exception:
                pass

        # TextField normalization (basic)
        if isinstance(control, ft.TextField):
            try:
                # Text color when unset or default
                if not getattr(control, "color", None):
                    control.color = colors.text_primary
                hs = getattr(control, "hint_style", None)
                if isinstance(hs, ft.TextStyle):
                    control.hint_style = ft.TextStyle(color=colors.text_secondary, size=getattr(hs, "size", None))
            except Exception:
                pass

        # Dropdown normalization
        if isinstance(control, ft.Dropdown):
            try:
                if not getattr(control, "color", None):
                    control.color = colors.text_primary
                if hasattr(control, "text_style"):
                    ts = getattr(control, "text_style", None)
                    size = getattr(ts, "size", None) if isinstance(ts, ft.TextStyle) else None
                    control.text_style = ft.TextStyle(color=colors.text_primary, size=size)
                if hasattr(control, "hint_style"):
                    hs = getattr(control, "hint_style", None)
                    size = getattr(hs, "size", None) if isinstance(hs, ft.TextStyle) else None
                    control.hint_style = ft.TextStyle(color=colors.text_secondary, size=size)
            except Exception:
                pass

        # Checkbox normalization
        if isinstance(control, ft.Checkbox):
            try:
                # Flet supports label_style in newer versions
                if hasattr(control, "label_style"):
                    ls = getattr(control, "label_style", None)
                    size = getattr(ls, "size", None) if isinstance(ls, ft.TextStyle) else None
                    control.label_style = ft.TextStyle(color=colors.text_primary, size=size)
            except Exception:
                pass

        # Recurse
        if hasattr(control, "content") and control.content is not None:
            apply_theme_to_control(control.content, colors)
        if hasattr(control, "controls") and control.controls:
            for c in list(control.controls):
                apply_theme_to_control(c, colors)
    except Exception:
        # Keep robust; do not break UI if some control misses attributes
        pass


def create_gradient_container(colors, content, height=None, padding=None, border_radius=12):
    """Create a modern gradient container"""
    return ft.Container(
        content=content,
        height=height,
        padding=padding or ft.padding.all(20),
        border_radius=border_radius,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[_adjust_hex(colors.gradient_start, -0.06), colors.gradient_start, colors.gradient_end, _adjust_hex(colors.gradient_end, 0.06)]
        ),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=colors.shadow,
            offset=ft.Offset(0, 4)
        )
    )


def create_glass_card(colors, content, height=None, padding=None, border_radius=16):
    """Create a modern glass morphism card"""
    return ft.Container(
        content=content,
        height=height,
        padding=padding or ft.padding.all(24),
        border_radius=border_radius,
        bgcolor=colors.glass_bg,
        border=ft.border.all(1, colors.border),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=30,
            color=colors.shadow,
            offset=ft.Offset(0, 8)
        )
    )


def create_modern_button(colors, text, icon=None, on_click=None, style="primary", width=None, height=40):
    """Create a modern animated button"""
    if style == "primary":
        bg_color = colors.button_primary
        text_color = colors.button_text
    elif style == "secondary":
        bg_color = colors.button_secondary
        text_color = colors.text_primary
    elif style == "success":
        bg_color = colors.success
        text_color = colors.button_text
    elif style == "danger":
        bg_color = colors.danger
        text_color = colors.button_text
    else:
        bg_color = colors.button_secondary
        text_color = colors.text_primary
    
    button_content = []
    if icon:
        button_content.append(ft.Icon(icon, color=text_color, size=18))
    button_content.append(ft.Text(text, color=text_color, weight=ft.FontWeight.W_600, size=14))
    
    return ft.Container(
        content=ft.Row(
            button_content,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        ),
        width=width,
        height=height,
        gradient=build_gradient(bg_color),
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        on_click=on_click,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=colors.shadow,
            offset=ft.Offset(0, 2)
        ),
        ink=True
    )


def create_stat_card(colors, title, value, icon, color_accent, on_click=None):
    """Create a modern stat card with hover animation"""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=color_accent, size=24),
                    width=48,
                    height=48,
                    bgcolor=f"{color_accent}20",
                    border_radius=12,
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text(title, size=12, color=colors.text_secondary, weight=ft.FontWeight.W_500)
                ], spacing=2, alignment=ft.CrossAxisAlignment.START)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=12),
        padding=ft.padding.all(20),
        bgcolor=colors.card_bg,
        border_radius=16,
        border=ft.border.all(1, colors.border),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=colors.shadow,
            offset=ft.Offset(0, 4)
        ),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        on_click=on_click,
        ink=True
    )


def create_modern_card(colors, content, padding=None, border_radius=16, elevation=1):
    """Create a modern card with subtle shadow"""
    shadow_blur = 8 if elevation == 1 else 16 if elevation == 2 else 24
    shadow_offset = 2 if elevation == 1 else 4 if elevation == 2 else 8

    return ft.Container(
        content=content,
        padding=padding or ft.padding.all(20),
        bgcolor=colors.card_bg,
        border_radius=border_radius,
        border=ft.border.all(1, colors.border),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=shadow_blur,
            color=colors.shadow,
            offset=ft.Offset(0, shadow_offset)
        )
    )
