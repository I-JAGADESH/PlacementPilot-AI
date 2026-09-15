import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Interview from "./pages/Interview";
import SkillIntelligence from "./pages/SkillIntelligence";
import ATSAnalyzer from "./pages/ATSAnalyzer";
import Roadmap from "./pages/Roadmap";
import Training from "./pages/Training";
import Assessment from "./pages/Assessment";

import "./App.css";

function App() {
  const token = localStorage.getItem("access_token");

  return (
    <BrowserRouter>
      <Routes>

        {/* Root */}
        <Route
          path="/"
          element={
            token ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Login */}
        <Route
          path="/login"
          element={
            token ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login />
            )
          }
        />

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={
            token ? (
              <Dashboard />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* My Profile */}
        <Route
          path="/profile"
          element={
            token ? (
              <Profile />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* ATS Analyzer */}
        <Route
          path="/ats"
          element={
            token ? (
              <ATSAnalyzer />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Skill Intelligence */}
        <Route
          path="/skill-intelligence"
          element={
            token ? (
              <SkillIntelligence />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Personalized Roadmap */}
        <Route
          path="/roadmap"
          element={
            token ? (
              <Roadmap />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Personalized Training */}
        <Route
          path="/training"
          element={
            token ? (
              <Training />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Skill Assessment */}
        <Route
          path="/assessment"
          element={
            token ? (
              <Assessment />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* AI Interview */}
        <Route
          path="/interview"
          element={
            token ? (
              <Interview />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Unknown routes */}
        <Route
          path="*"
          element={
            <Navigate to="/" replace />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;