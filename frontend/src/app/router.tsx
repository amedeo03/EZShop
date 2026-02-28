import { createBrowserRouter, Navigate } from "react-router-dom";
import Layout from "../shared/components/Layout";
import LoginPage from "../pages/login/LoginPage";
import DashboardPage from "../pages/dashboard/DashboardPage";
import ProductsPage from "../pages/products/ProductsPage";

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
      { path: "Dashboard", element: <DashboardPage /> },
      { path: "Products", element: <ProductsPage /> },
    ],
  }
]);