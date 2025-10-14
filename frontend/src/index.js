import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import * as serviceWorkerRegistration from './serviceWorkerRegistration';

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <App />
);

// Register service worker for PWA functionality
// TEMPORARILY DISABLED to fix cache issues
serviceWorkerRegistration.unregister();

