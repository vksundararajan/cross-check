import mesop as me

class Styles:
    # -------------------------------- App Layouts ------------------------------- #
    APP_CONTAINER = me.Style(
        padding=me.Padding.all(24), 
        max_width=1000, 
        margin=me.Margin.symmetric(horizontal="auto")
    )

    APP_HEADER = me.Style(display="flex", justify_self="center")

    INPUT_ROW = me.Style(
        display="flex", 
        gap=24, 
        align_items="baseline", 
        justify_content="center", 
        margin=me.Margin(bottom=32)
    )

    INPUT_FIELD = me.Style(flex_grow=1)
    TOGGLE_BOX = me.Style(display="flex", align_items="center", gap=10)

    GRID_LAYOUT = me.Style(
        display="grid", 
        grid_template_columns="repeat(auto-fit, minmax(350px, 1fr))", 
        gap=24, 
        margin=me.Margin(bottom=32)
    )

    CARD_HEADER = me.Style(display="flex", align_items="center", gap=12)
    CARD_TITLE_BOX = me.Style(flex_grow=1)
    CARD_TITLE_TEXT = me.Style(font_weight="bold", padding=me.Padding(top=10))
    SPINNER_BOX = me.Style(padding=me.Padding.symmetric(vertical=20))

    # ---------------------------------- Methods --------------------------------- #
    @staticmethod
    def get_status_color(status):
        if status == "PHISHING": return me.theme_var("error-container")
        elif status == "LEGITIMATE": return me.theme_var("primary-container")
        elif status == "UNCERTAIN": return me.theme_var("secondary-container")
        return me.theme_var("surface-container-highest")

    @staticmethod
    def get_status_text_color(status):
        if status == "PHISHING": return me.theme_var("on-error-container")
        elif status == "LEGITIMATE": return me.theme_var("on-primary-container")
        return me.theme_var("on-surface")

    @staticmethod
    def card_container(status):
        return me.Style(
            background=Styles.get_status_color(status),
            color=Styles.get_status_text_color(status),
            border_radius=16,
            padding=me.Padding.all(16),
            display="flex",
            flex_direction="column",
            gap=8
        )

    @staticmethod
    def verdict_box(verdict):
        if verdict == "PHISHING":
            verdict_color = "#d32f2f"
        elif verdict == "LEGITIMATE":
            verdict_color = "#388e3c"
        elif verdict in ("INVALID URL", "RATE LIMIT", "REQUEST TOO LARGE", "ERROR"):
            verdict_color = "#f57c00"
        else:
            verdict_color = "#757575"
        return me.Style(
            background=verdict_color, 
            color="white", 
            padding=me.Padding.all(24), 
            border_radius=12, 
            text_align="center"
        )

styles = Styles()