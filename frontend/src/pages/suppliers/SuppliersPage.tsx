import React from "react";
import { Typography, Box, Paper, Button, TextField, Grid } from "@mui/material";

export default function SuppliersPage() {
  return (
    <>
      <Grid container alignItems="center" justifyContent="space-between">
        <Grid item>
          <Typography variant="h4" gutterBottom>
            Suppliers
          </Typography>
        </Grid>
        <Grid item>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField size="small" placeholder="Search suppliers..." />
            <Button variant="contained">New Supplier</Button>
          </Box>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2 }}>
        <Paper sx={{ height: 420, p: 2 }}>Suppliers table placeholder</Paper>
      </Box>
    </>
  );
}
