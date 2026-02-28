import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Card,
  Link,
  Alert,
} from "@mui/material";

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password");
      return;
    }

    setLoading(true);

    try {
      // TODO: Replace with actual API call
      // For now, just simulate a successful login
      console.log("Login attempt:", { username, password });
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Navigate to dashboard on successful login
      navigate("/Dashboard");
    } catch (err) {
      setError("Login failed. Please try again.");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = () => {
    // TODO: Implement register navigation
    console.log("Navigate to register page");
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        bgcolor: "#f5f5f5",
      }}
    >
      <Container maxWidth="sm">
        <Card sx={{ p: 4 }}>
          {/* Header */}
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{ textAlign: "center", mb: 3, fontWeight: 600 }}
          >
            EZShop Login
          </Typography>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <Box component="form" onSubmit={handleLogin}>
            {/* Username Input */}
            <TextField
              fullWidth
              label="Username"
              variant="outlined"
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoFocus
            />

            {/* Password Input */}
            <TextField
              fullWidth
              label="Password"
              type="password"
              variant="outlined"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              sx={{ mb: 3 }}
            />

            {/* Login Button */}
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              type="submit"
              disabled={loading}
              sx={{ mb: 2 }}
            >
              {loading ? "Logging in..." : "Login"}
            </Button>
          </Box>

          {/* Register Link */}
          <Box sx={{ textAlign: "center" }}>
            <Typography variant="body2" color="textSecondary">
              Don't have an account?{" "}
              <Link
                component="button"
                type="button"
                onClick={handleRegister}
                sx={{ cursor: "pointer", fontWeight: 600 }}
              >
                Register here
              </Link>
            </Typography>
          </Box>
        </Card>
      </Container>
    </Box>
  );
}
