"""
Standalone helper copied from the working demo.

Usage
-----
from streamlit_push_notifications import send_push
send_push(sound_path="https://…/beep.mp3")
"""
from streamlit import runtime
from streamlit.components.v1 import html


def send_push(
    title: str = "Pass TITLE as an argument 🔥",
    body: str = "Pass BODY as an argument 👨🏻‍💻",
    icon_path: str = "",
    sound_path: str = "https://cdn.pixabay.com/audio/2024/02/19/audio_e4043ea6be.mp3",
    only_when_on_other_tab: bool = False,
    tag: str = "",
) -> None:
    # ------------------------------------------------------------------ #
    # Upload media to Streamlit’s static file server (when possible)
    # ------------------------------------------------------------------ #
    try:
        icon_path_on_server = runtime.get_instance().media_file_mgr.add(
            icon_path, "image/png", ""
        )
    except Exception:
        icon_path_on_server = ""

    try:
        sound_path_on_server = runtime.get_instance().media_file_mgr.add(
            sound_path, mimetype="audio/mpeg", coordinates="1.(3.-14).5"
        )
    except Exception:
        sound_path_on_server = sound_path  # fall back to original URL

    # ------------------------------------------------------------------ #
    # JS variables
    # ------------------------------------------------------------------ #
    variables = f"""
    var title = `{title}`;
    var body  = `{body}`;
    var icon  = `{icon_path_on_server}`;
    var audio = `{sound_path_on_server}`;
    var tag   = `{tag}`;
    var notificationSent = false;
    """

    # ------------------------------------------------------------------ #
    # JS logic – ask for permission, fire Notification, play sound
    # ------------------------------------------------------------------ #
    core_script = """
    Notification.requestPermission().then(perm => {
        if (perm === 'granted') {
            notification = new Notification(title, {
                body: body,
                icon: icon,
                tag: tag
            });
            new Audio(audio).play();
            notificationSent = true;
        } else if (perm === 'denied') {
            console.log('Notification permission denied');
        } else {
            console.log('Notification permission default/unknown');
        }
    }).catch(err => console.error('Notification error:', err));
    """

    # Optional “only play when tab is hidden” wrapper
    if only_when_on_other_tab:
        core_script = f"""
        let notification;
        document.addEventListener("visibilitychange", () => {{
            if (document.visibilityState === "hidden" && !notificationSent) {{{core_script}}}
            else if (document.visibilityState === "visible") {{
                if (notification) notification.close();
                notificationSent = false;
            }}
        }});
        """

    html(f"<script>{variables}{core_script}</script>", width=0, height=0)


def send_alert(message: str = "") -> None:
    html(f"<script>window.alert(`{message}`)</script>", width=0, height=0)
