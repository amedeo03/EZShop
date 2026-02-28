import { createBrowserRouter, Navigate } from "react-router-dom";
import Layout from "../shared/components/Layout";
import LoginPage from "../pages/login/LoginPage";
import OverviewPage from "../pages/overview/OverviewPage";
import SalesPage from "../pages/sales/SalesPage";
import InventoryPage from "../pages/inventory/InventoryPage";
import SuppliersPage from "../pages/suppliers/SuppliersPage";
import OrdersPage from "../pages/orders/OrdersPage";
import AnalyticsPage from "../pages/analytics/AnalyticsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/Login" replace />,
  },
  {
    path: "/Login",
    element: <LoginPage />,
  },
  {
    path: "/",
    element: <Layout />,
    children: [
      { path: "Overview", element: <OverviewPage /> },
      { path: "Sales", element: <SalesPage /> },
      { path: "Inventory", element: <InventoryPage /> },
      { path: "Suppliers", element: <SuppliersPage /> },
      { path: "Orders", element: <OrdersPage /> },
      { path: "Analytics", element: <AnalyticsPage /> }
    ],
  }
]);