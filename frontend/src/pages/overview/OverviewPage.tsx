import { Typography, Grid, Paper, Box } from "@mui/material";

export default function OverviewPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>
        Overview
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>Today's Sales: --</Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>Ongoing Orders: --</Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>Inventory Alerts: --</Paper>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ mt: 2 }}>
            <Paper sx={{ height: 300, p: 2 }}>Overview panels / widgets</Paper>
          </Box>
        </Grid>
      </Grid>
    </>
  );
}
