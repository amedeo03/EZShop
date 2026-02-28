import React from "react";
import {
  Typography,
  Box,
  Paper,
  Button,
  TextField,
  Grid,
} from "@mui/material";

export default function SalesPage() {
  return (
    <>
      <Grid container alignItems="center" justifyContent="space-between">
        <Grid item>
          <Typography variant="h4" gutterBottom>
            Sales
          </Typography>
        </Grid>
        <Grid item>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField size="small" placeholder="Search sales..." />
            <Button variant="contained">New Sale</Button>
          </Box>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2 }}>
        <Paper sx={{ height: 420, p: 2 }}>Sales table placeholder</Paper>
      </Box>
    </>
  );
}
