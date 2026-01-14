import { useEffect } from 'react';

const HeyGenAvatar = () => {
  useEffect(() => {
    const host = "https://labs.heygen.com";
    const url =
      host +
      "/guest/streaming-embed?share=eyJxdWFsaXR5IjoiaGlnaCIsImF2YXRhck5hbWUiOiJEZXh0ZXJfRG9jdG9yX1NpdHRpbmcyX3B1%0D%0AYmxpYyIsInByZXZpZXdJbWciOiJodHRwczovL2ZpbGVzMi5oZXlnZW4uYWkvYXZhdGFyL3YzL2Y4%0D%0AM2ZmZmM0NWZhYTQzNjhiNmRiOTU5N2U2YjMyM2NhXzQ1NTkwL3ByZXZpZXdfdGFsa18zLndlYnAi%0D%0ALCJuZWVkUmVtb3ZlQmFja2dyb3VuZCI6ZmFsc2UsImtub3dsZWRnZUJhc2VJZCI6Ijk0MzIzOTA4%0D%0AYzgzNDQ5Mjg5YWY4N2MyODlhZTJmZDMwIiwidXNlcm5hbWUiOiI0MmE3OTNhZTJjMjk0OWNlYTE1%0D%0AYmI5MjhjMGZlMmFkMSJ9&inIFrame=1";

    const clientWidth = document.body.clientWidth;

    const wrapDiv = document.createElement("div");
    wrapDiv.id = "heygen-streaming-embed";

    const container = document.createElement("div");
    container.id = "heygen-streaming-container";

    const stylesheet = document.createElement("style");
    stylesheet.innerHTML = `
      #heygen-streaming-embed {
        z-index: 9999;
        position: fixed;
        left: 40px;
        bottom: 40px;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        border: 2px solid #fff;
        box-shadow: 0px 8px 24px 0px rgba(0, 0, 0, 0.12);
        transition: all linear 0.1s;
        overflow: hidden;
        opacity: 0;
        visibility: hidden;
      }
      #heygen-streaming-embed.show {
        opacity: 1;
        visibility: visible;
      }
      #heygen-streaming-embed.expand {
        ${
          clientWidth < 540
            ? "height: 266px; width: 96%; left: 50%; transform: translateX(-50%);"
            : "height: 366px; width: calc(366px * 16 / 9);"
        }
        border: 0;
        border-radius: 8px;
      }
      #heygen-streaming-container {
        width: 100%;
        height: 100%;
      }
      #heygen-streaming-container iframe {
        width: 100%;
        height: 100%;
        border: 0;
      }
    `;

    const iframe = document.createElement("iframe");
    iframe.allowFullscreen = false;
    iframe.title = "Streaming Embed";
    iframe.role = "dialog";
    iframe.allow = "microphone";
    iframe.src = url;

    let visible = false;
    let initial = false;

    const messageHandler = (e) => {
      if (
        e.origin === host &&
        e.data &&
        e.data.type === "streaming-embed"
      ) {
        if (e.data.action === "init") {
          initial = true;
          wrapDiv.classList.toggle("show", initial);
        } else if (e.data.action === "show") {
          visible = true;
          wrapDiv.classList.toggle("expand", visible);
        } else if (e.data.action === "hide") {
          visible = false;
          wrapDiv.classList.toggle("expand", visible);
        }
      }
    };

    window.addEventListener("message", messageHandler);

    container.appendChild(iframe);
    wrapDiv.appendChild(stylesheet);
    wrapDiv.appendChild(container);
    document.body.appendChild(wrapDiv);

    // Cleanup on component unmount
    return () => {
      window.removeEventListener("message", messageHandler);
      document.body.removeChild(wrapDiv);
    };
  }, []);

  return null; // Nothing is rendered by this component directly
};

export default HeyGenAvatar;
