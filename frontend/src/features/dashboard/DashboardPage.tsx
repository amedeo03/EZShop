import { Typography, Paper, Grid } from "@mui/material";

export default function DashboardPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2 }}>Total Products: --</Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2 }}>Total Sales: --</Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2 }}>Low Stock Alerts: --</Paper>
        </Grid>
      </Grid>
    </>
  );
}