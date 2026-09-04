import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Run from "./pages/Run";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/run" element={<Run />} />
    </Routes>
  );
}
