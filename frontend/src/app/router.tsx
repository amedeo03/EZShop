import { createBrowserRouter } from "react-router-dom";
import Layout from "../shared/components/Layout";
import LoginPage from "../features/auth/LoginPage";
import DashboardPage from "../features/dashboard/DashboardPage";
import ProductsPage from "../features/products/ProductsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "products", element: <ProductsPage /> },
    ],
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
]);