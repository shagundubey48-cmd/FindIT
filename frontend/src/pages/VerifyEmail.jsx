
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import authService from "../services/authService";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function VerifyEmail() {
  const { token } = useParams();

  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("Verifying your email...");

  useEffect(() => {
    let active = true;

    const verify = async () => {
      try {
        const response = await authService.verifyEmail(token);

        if (active) {
          setStatus("success");
          setMessage(
            response.message || "Email verified successfully!"
          );
        }
      } catch (error) {
        if (active) {
          setStatus("error");
          setMessage(
            error.response?.data?.message ||
            "Email verification failed."
          );
        }
      }
    };

    verify();

    return () => {
      active = false;
    };
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">

      <div className="bg-white shadow-lg rounded-2xl p-10 text-center max-w-md w-full">

        <Link to="/" className="text-3xl font-bold text-primary">
          FindIT.
        </Link>

        <div className="flex justify-center mt-10 mb-5">

          {status === "loading" && (
            <Loader2 size={60} className="text-primary animate-spin" />
          )}

          {status === "success" && (
            <CheckCircle size={60} className="text-green-500" />
          )}

          {status === "error" && (
            <XCircle size={60} className="text-red-500" />
          )}

        </div>

        <h2 className="text-2xl font-bold">
          {status === "loading" && "Verifying Email"}
          {status === "success" && "Email Verified!"}
          {status === "error" && "Verification Failed"}
        </h2>

        <p className="text-gray-500 mt-4">
          {message}
        </p>

        {status === "success" && (
          <Link
            to="/login"
            className="inline-block mt-7 bg-primary text-white px-7 py-3 rounded-lg"
          >
            Continue to Login
          </Link>
        )}

        {status === "error" && (
          <Link
            to="/login"
            className="inline-block mt-7 border border-primary text-primary px-7 py-3 rounded-lg"
          >
            Go to Login
          </Link>
        )}

      </div>
    </div>
  );
}

