import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import LostItems from "./pages/LostItems";
import FoundItems from "./pages/FoundItems";
import ReportLost from "./pages/ReportLost";
import ReportFound from "./pages/ReportFound";
import ItemDetails from "./pages/ItemDetails";
import MyReports from "./pages/MyReports";
import MyClaims from "./pages/MyClaims";
import MyHandovers from "./pages/MyHandovers";
import Messages from "./pages/Messages";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import Feedback from "./pages/Feedback";
import MatchedItems from "./pages/MatchedItems";
import ClaimDetails from "./pages/ClaimDetails";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminStatistics from "./pages/admin/AdminStatistics";
import ClaimReview from "./pages/admin/ClaimReview";
import ManageClaims from "./pages/admin/ManageClaims";
import ManageItems from "./pages/admin/ManageItems";
import ManageUsers from "./pages/admin/ManageUsers";
import UnclaimedItems from "./pages/admin/UnclaimedItems";

function GuestRoute(){const {isAuthenticated,loading}=useAuth();if(loading)return <div className="p-10 text-center">Loading...</div>;return isAuthenticated?<Navigate to="/dashboard" replace/>:<Outlet/>;}
function Layout(){return <><Navbar/><Outlet/><Footer/></>;}
function NotFound(){return <main className="p-20 text-center"><h1 className="text-3xl font-bold">404 – Page not found</h1><a href="/" className="mt-4 inline-block text-indigo-600">Go home</a></main>;}
export default function App(){return <Routes><Route element={<Layout/>}>
<Route index element={<Home/>}/><Route path="lost-items" element={<LostItems/>}/><Route path="found-items" element={<FoundItems/>}/>
<Route element={<GuestRoute/>}><Route path="login" element={<Login/>}/><Route path="register" element={<Register/>}/></Route>
<Route path="verify-email" element={<VerifyEmail/>}/>
<Route element={<ProtectedRoute/>}>
<Route path="dashboard" element={<Dashboard/>}/><Route path="report-lost" element={<ReportLost/>}/><Route path="report-found" element={<ReportFound/>}/><Route path="my-reports" element={<MyReports/>}/><Route path="items/:id" element={<ItemDetails/>}/><Route path="matched-items" element={<MatchedItems/>}/><Route path="claims/:id" element={<ClaimDetails/>}/><Route path="my-claims" element={<MyClaims/>}/><Route path="my-handovers" element={<MyHandovers/>}/><Route path="messages" element={<Messages/>}/><Route path="notifications" element={<Notifications/>}/><Route path="profile" element={<Profile/>}/><Route path="feedback" element={<Feedback/>}/>
</Route>
<Route element={<AdminRoute/>}><Route path="admin" element={<AdminDashboard/>}/><Route path="admin/statistics" element={<AdminStatistics/>}/><Route path="admin/claims" element={<ManageClaims/>}/><Route path="admin/claims/review" element={<ClaimReview/>}/><Route path="admin/items" element={<ManageItems/>}/><Route path="admin/users" element={<ManageUsers/>}/><Route path="admin/unclaimed" element={<UnclaimedItems/>}/></Route>
<Route path="*" element={<NotFound/>}/></Route></Routes>;}
