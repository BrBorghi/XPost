# xpost.py
# Simple Streamlit app to post on X with text and optional post quote via URL, protected by password.
# Needs a X developper account to get API, API secret, Access Token, Access Token secret

import streamlit as st
import hmac  # For secure password comparison - protection against timing attacks
import tweepy
import re  # For a simple regex in extraction
import tomllib  # For loading config.toml


def load_credentials():
    """
    Loads X credentials from st.secrets

    CONSUMER_KEY = your_api_key
    CONSUMER_SECRET = your_api_secret
    ACCESS_TOKEN = your_access_token
    ACCESS_TOKEN_SECRET = your_access_token_secret
    """
    return {
        "consumer_key": st.secrets["CONSUMER_KEY"],
        "consumer_secret": st.secrets["CONSUMER_SECRET"],
        "access_token": st.secrets["ACCESS_TOKEN"],
        "access_token_secret": st.secrets["ACCESS_TOKEN_SECRET"],
    }


def load_config():
    """
    Loads configuration from config.toml and overrides with st.secrets["config"] if present

    Example of config.toml:
    [config]
    page_title = "xpost"
    textarea_max_chars = 280
    textarea_height = 100
    textarea_font_size = 16

    Returns the flattened 'config' dict for simple access in the app.
    """
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)["config"]

    try:
        config.update(st.secrets["config"])
    except KeyError:
        pass  # No [config] section in secrets.toml, use config.toml defaults

    return config


def post_message(client, message):
    """
    Posts a simple message on X.
    """
    try:
        response = client.create_tweet(text=message)
        return response
    except tweepy.TweepyException:
        raise


def extract_tweet_id_from_url(url):
    """
    Extracts the ID of an X post from a URL.
    Uses a regex for robustness.
    Built-in validation to prevent error propagation in posting.
    Example: 'https://x.com/user/status/123456789' -> '123456789'
    """
    pattern = r"https?://(?:www\.)?(?:x\.com|twitter\.com)/[^/]+/status/(\d+)"
    match = re.match(pattern, url)
    if match:
        tweet_id = match.group(1)
        if tweet_id.isdigit():
            return tweet_id
    raise ValueError(f"Invalid URL or does not contain a valid post ID: {url}")


def post_quote(client, message, quote_tweet_id_or_url):
    """
    Posts a message that quotes another post on X.
    quote may be the id of the mother post or the entire url of the post
    """
    # Detection and extraction if it's a URL
    if quote_tweet_id_or_url.startswith("http"):
        quote_tweet_id = extract_tweet_id_from_url(quote_tweet_id_or_url)
    else:
        quote_tweet_id = quote_tweet_id_or_url

    if not isinstance(quote_tweet_id, str) or not quote_tweet_id.isdigit():
        raise ValueError(
            "quote_tweet_id must be a string representing a valid numeric ID."
        )

    try:
        response = client.create_tweet(text=message, quote_tweet_id=quote_tweet_id)
        return response
    except tweepy.TweepyException:
        raise


def check_password():
    """Checks the entered password against the APP_PASSWORD define in the secrets. Returns True if OK."""

    def password_entered():
        """Form callback – compares securely."""
        if hmac.compare_digest(
            st.session_state["password_input"], st.secrets["APP_PASSWORD"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # Cleanup for security
        else:
            st.session_state["password_correct"] = False
            del st.session_state["password_input"]

    # If already authenticated, skip
    if st.session_state.get("password_correct", False):
        return True

    # Display login form
    st.title("🔒 Reserved access")
    st.markdown("Sign-in:")

    with st.form(key="password_form"):
        st.text_input("Password", type="password", key="password_input")
        submit = st.form_submit_button("Submit")

    if submit:
        password_entered()

    if not st.session_state.get("password_correct", False):
        st.error("😕 Incorrect password")
        st.stop()  # Blocks execution here if false

    return True


def main():
    # Load config first
    config = load_config()

    # Page config – must be the first Streamlit call
    st.set_page_config(
        page_title=config["page_title"],  # Custom title for browser tab
        page_icon="🛡️",  # Emoji or URL for favicon (hard coded !)
    )

    # CSS to customize text_area font size (dynamic from config)
    css = f"""
    <style>
        textarea {{
            font-size: {config["textarea_font_size"]}px !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Password check before displaying main content
    # check_password is called early, blocks with st.stop() if failure
    if check_password():
        # Load creds and client once (only if auth OK)
        creds = load_credentials()
        client = tweepy.Client(
            consumer_key=creds["consumer_key"],
            consumer_secret=creds["consumer_secret"],
            access_token=creds["access_token"],
            access_token_secret=creds["access_token_secret"],
        )

        # Main content
        st.title("Post on X")
        st.markdown("Enter the text and optionally a URL to quote.")

        text = st.text_area(
            f"Post text (max {config['textarea_max_chars']} chars)",
            max_chars=config["textarea_max_chars"],
            height=config["textarea_height"],
        )

        quote_url = st.text_input(
            "URL of the post to quote (optional)",
            placeholder="https://x.com/.../status/...",
        )

        if st.button("Post on X"):
            if not text:
                st.error("The text cannot be empty!")
            else:
                try:
                    if quote_url:
                        response = post_quote(client, text, quote_url)
                    else:
                        response = post_message(client, text)
                    st.success(f"Posted successfully! ID: {response.data['id']}")
                except ValueError as ve:
                    st.error(f"Validation error: {ve}")
                except Exception as e:
                    st.error(f"Error during posting: {e}")

        if st.button("Logout"):
            for key in ["password_correct"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
