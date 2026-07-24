from urllib.parse import urlparse

import streamlit as st
import streamlit.components.v1 as components
import streamlit.components.v1 as components


st.set_page_config(
    page_title="NeuroVoice",
    page_icon="assets/neurovoice_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)


components.html(
    """
    <script>
    (() => {
        const win = window.parent;
        const doc = win.document;

        const LOADER_ID = "nv-safe-page-loader";
        const STYLE_ID = "nv-safe-page-loader-style";

        function removeLoader() {
            const loader = doc.getElementById(LOADER_ID);

            if (loader) {
                loader.remove();
            }
        }

        function installStyles() {
            if (doc.getElementById(STYLE_ID)) {
                return;
            }

            const style = doc.createElement("style");
            style.id = STYLE_ID;

            style.textContent = `
                #${LOADER_ID} {
                    position: fixed;
                    inset: 0;
                    z-index: 2147483647;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: rgba(7, 17, 31, 0.82);
                    backdrop-filter: blur(7px);
                    -webkit-backdrop-filter: blur(7px);
                    pointer-events: none;
                }

                #${LOADER_ID} .nv-loader-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 24px;
                }

                #${LOADER_ID} .nv-loader-text {
                    color: #ffffff;
                    font-family:
                        Inter,
                        system-ui,
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        sans-serif;
                    font-size: 28px;
                    font-weight: 750;
                }

                #${LOADER_ID} .nv-loader-ring {
                    width: 92px;
                    height: 92px;
                    border-radius: 50%;

                    background: conic-gradient(
                        from 0deg,
                        rgba(145, 167, 255, 0.10),
                        #91a7ff,
                        #7f6df2,
                        #55d7d0,
                        rgba(85, 215, 208, 0.10)
                    );

                    -webkit-mask:
                        radial-gradient(
                            farthest-side,
                            transparent calc(100% - 15px),
                            #000 calc(100% - 14px)
                        );

                    mask:
                        radial-gradient(
                            farthest-side,
                            transparent calc(100% - 15px),
                            #000 calc(100% - 14px)
                        );

                    animation:
                        nv-loader-spin 2.8s linear infinite,
                        nv-loader-color 5.6s ease-in-out infinite;
                }

                @keyframes nv-loader-spin {
                    from {
                        transform: rotate(0deg);
                    }

                    to {
                        transform: rotate(360deg);
                    }
                }

                @keyframes nv-loader-color {
                    0%,
                    100% {
                        filter: hue-rotate(0deg);
                    }

                    50% {
                        filter: hue-rotate(28deg);
                    }
                }
            `;

            doc.head.appendChild(style);
        }

        function showLoader() {
            removeLoader();
            installStyles();

            const loader = doc.createElement("div");
            loader.id = LOADER_ID;

            loader.innerHTML = `
                <div class="nv-loader-content">
                    <div class="nv-loader-text">Loading</div>
                    <div class="nv-loader-ring"></div>
                </div>
            `;

            doc.body.appendChild(loader);
        }

        removeLoader();
        installStyles();

        if (win.__nvSafeLoaderHandler) {
            doc.removeEventListener(
                "pointerdown",
                win.__nvSafeLoaderHandler,
                true
            );
        }

        win.__nvSafeLoaderHandler = event => {
            const link = event.target.closest(".nv-links a");

            if (!link) {
                return;
            }

            const destination = new URL(
                link.href,
                win.location.href
            );

            if (
                destination.pathname === win.location.pathname &&
                destination.search === win.location.search
            ) {
                return;
            }

            showLoader();
        };

        doc.addEventListener(
            "pointerdown",
            win.__nvSafeLoaderHandler,
            true
        );

        win.addEventListener("pageshow", removeLoader);
    })();
    </script>
    """,
    height=0,
    width=0,
)



current_path = urlparse(st.context.url).path.rstrip("/")

if current_path == "":
    current_path = "/"


def nav_class(path: str) -> str:
    return "active" if current_path == path else ""


st.html(
    f"""
<style>
.stApp {{
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(73, 103, 255, 0.16),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 5%,
            rgba(130, 85, 255, 0.14),
            transparent 26%
        ),
        linear-gradient(
            180deg,
            #07111f 0%,
            #0a1525 55%,
            #07111f 100%
        );
}}

.block-container {{
    max-width: 1180px;
    padding-top: 6.5rem;
    padding-bottom: 4rem;
}}

[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stNavigation"] {{
    display: none;
}}

header {{
    background: transparent !important;
}}

#MainMenu,
footer {{
    visibility: hidden;
}}

.nv-header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 74px;
    z-index: 999999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4.5rem;
    background: rgba(7, 17, 31, 0.97);
    border-bottom: 1px solid rgba(255, 255, 255, 0.10);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.22);
    backdrop-filter: blur(18px);
}}

.nv-brand {{
    color: white;
    font-size: 1.4rem;
    font-weight: 850;
    letter-spacing: -0.045em;
    white-space: nowrap;
}}

.nv-brand span {{
    color: #91a7ff;
}}

.nv-links {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.45rem;
}}

.nv-links a {{
    color: #aebbd0;
    text-decoration: none;
    font-size: 0.94rem;
    font-weight: 650;
    white-space: nowrap;
    padding: 0.66rem 0.95rem;
    border-radius: 11px;
    border: 1px solid transparent;
    transition:
        color 0.18s ease,
        background 0.18s ease,
        border-color 0.18s ease,
        box-shadow 0.18s ease,
        transform 0.18s ease;
}}

.nv-links a:hover {{
    color: #ffffff;
    background: rgba(143, 165, 255, 0.11);
    border-color: rgba(143, 165, 255, 0.18);
    transform: translateY(-1px);
}}

.nv-links a.active {{
    color: #ffffff;
    background: linear-gradient(
        135deg,
        rgba(88, 113, 255, 0.95),
        rgba(121, 82, 235, 0.95)
    );
    border-color: rgba(189, 200, 255, 0.60);
    box-shadow:
        0 7px 22px rgba(68, 78, 210, 0.40),
        inset 0 1px 0 rgba(255, 255, 255, 0.18);
}}

.nv-links a.active:hover {{
    background: linear-gradient(
        135deg,
        rgba(101, 125, 255, 1),
        rgba(135, 93, 245, 1)
    );
}}

@media (max-width: 900px) {{
    .nv-header {{
        padding: 0 1.2rem;
    }}

    .nv-links {{
        gap: 0.08rem;
    }}

    .nv-links a {{
        padding: 0.55rem 0.48rem;
        font-size: 0.76rem;
    }}

    .nv-brand {{
        font-size: 1.05rem;
    }}
}}
</style>

<div class="nv-header">
    <div class="nv-brand">
        Neuro<span>Voice</span>
    </div>

    <div class="nv-links">
        <a
            href="/"
            target="_self"
            class="{nav_class('/')}"
        >
            Home
        </a>

        <a
            href="/test"
            target="_self"
            class="{nav_class('/test')}"
        >
            Take Test
        </a>

        <a
            href="/how_it_works"
            target="_self"
            class="{nav_class('/how_it_works')}"
        >
            How It Works
        </a>

        <a
            href="/project"
            target="_self"
            class="{nav_class('/project')}"
        >
            Research & Data
        </a>

        <a
            href="/about"
            target="_self"
            class="{nav_class('/about')}"
        >
            About
        </a>
    </div>
</div>
"""
)


pages = [
    st.Page(
        "views/home.py",
        title="Home",
        default=True,
    ),
    st.Page(
        "views/test.py",
        title="Take Test",
        url_path="test",
    ),
    st.Page(
        "views/memory.py",
        title="Optional Memory Challenge",
        url_path="memory",
    ),
    st.Page(
        "views/how_it_works.py",
        title="How It Works",
        url_path="how_it_works",
    ),
    st.Page(
        "views/project.py",
        title="Research & Data",
        url_path="project",
    ),
    st.Page(
        "views/about.py",
        title="About",
        url_path="about",
    ),
]


navigation = st.navigation(
    pages,
    position="hidden",
)

navigation.run()

