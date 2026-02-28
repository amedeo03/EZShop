import { createBrowserRouter } from "react-router-dom";
import Layout from "../shared/components/Layout";
import LoginPage from "../pages/login/LoginPage";
import DashboardPage from "../pages/dashboard/DashboardPage";
import ProductsPage from "../pages/products/ProductsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { path: "Login", element: <LoginPage /> },
      { path: "Dashboard", element: <DashboardPage /> },
      { path: "Products", element: <ProductsPage /> },
    ],
  }
]);