import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
export default function AdminRoute(){const {user,loading,isAuthenticated}=useAuth();if(loading)return <div className="p-10 text-center">Loading...</div>;return isAuthenticated&&user?.is_admin?<Outlet/>:<Navigate to="/dashboard" replace/>;}

