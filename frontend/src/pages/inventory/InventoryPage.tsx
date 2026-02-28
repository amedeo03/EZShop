import React from "react";
import { Typography, Box, Paper, Button, TextField, Grid } from "@mui/material";

export default function InventoryPage() {
  return (
    <>
      <Grid container alignItems="center" justifyContent="space-between">
        <Grid item>
          <Typography variant="h4" gutterBottom>
            Inventory
          </Typography>
        </Grid>
        <Grid item>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField size="small" placeholder="Search products..." />
            <Button variant="contained">New Product</Button>
          </Box>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2 }}>
        <Paper sx={{ height: 420, p: 2 }}>Inventory table placeholder</Paper>
      </Box>
    </>
  );
}
