import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./tw-local.css";    // or ./index.css if you use built file

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
