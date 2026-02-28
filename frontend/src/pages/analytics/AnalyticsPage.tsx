import React from "react";
import { Typography, Box, Paper, ButtonGroup, Button } from "@mui/material";

export default function AnalyticsPage() {
  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h4" gutterBottom>
          Analytics
        </Typography>

        <ButtonGroup variant="outlined">
          <Button>Last 7 days</Button>
          <Button>Last 30 days</Button>
          <Button>Last year</Button>
        </ButtonGroup>
      </div>

      <Box sx={{ mt: 2 }}>
        <Paper sx={{ height: 380, p: 2 }}>Chart placeholder</Paper>
      </Box>
    </>
  );
}
