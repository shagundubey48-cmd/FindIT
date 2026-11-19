import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getClaim,
  getHandoverQr,
  submitClaimEvidence,
} from "../services/claimService";
import Loader from "../components/Loader";
import { PROOF_TYPES } from "../utils/constants";
import {
  formatDateTime,
  getErrorMessage,
  openBlobInNewTab,
  statusClasses,
  titleCase,
} from "../utils/helpers";

export default function ClaimDetails() {
  const { id } = useParams();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const [proofType, setProofType] = useState("identifying_mark");
  const [proofDetails, setProofDetails] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const { data } = await getClaim(id);
      setClaim(data.claim);
      setProofType(data.claim.proof_type || "identifying_mark");
      setProofDetails(data.claim.proof_details || "");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const handleEvidence = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    try {
      setSaving(true);
      await submitClaimEvidence(id, {
        proof_type: proofType,
        proof_details: proofDetails,
      });
      setNotice("Evidence saved.");
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const showQr = async () => {
    try {
      const { data } = await getHandoverQr(id);
      openBlobInNewTab(data);
    } catch (err) {
      // Error bodies arrive as blobs when responseType is "blob".
      try {
        const text = await err.response.data.text();
        setError(JSON.parse(text).message);
      } catch {
        setError(getErrorMessage(err));
      }
    }
  };

  if (loading) return <Loader />;

  if (!claim) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-10">
        <p className="rounded-lg bg-red-50 p-3 text-red-700">{error || "Claim not found."}</p>
        <Link to="/my-claims" className="mt-4 inline-block text-primary">Back to my claims</Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-5 py-10">
      <Link to="/my-claims" className="text-sm text-primary">← My claims</Link>

      <div className="mt-4 rounded-2xl border bg-white p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold">{claim.item_title}</h1>
            <Link to={`/items/${claim.item_id}`} className="text-sm text-primary">View item</Link>
          </div>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(claim.status)}`}>
            {titleCase(claim.status)}
          </span>
        </div>

        {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}
        {notice && <p className="mt-4 rounded-lg bg-green-50 p-3 text-green-700">{notice}</p>}

        <dl className="mt-6 space-y-4 text-sm">
          <div>
            <dt className="font-medium text-slate-500">Ownership details</dt>
            <dd className="mt-1 whitespace-pre-wrap">{claim.ownership_details}</dd>
          </div>
          <div>
            <dt className="font-medium text-slate-500">Status last updated</dt>
            <dd className="mt-1">{formatDateTime(claim.status_updated_at)}</dd>
          </div>
          {claim.admin_remarks && (
            <div>
              <dt className="font-medium text-slate-500">Administrator remarks</dt>
              <dd className="mt-1">{claim.admin_remarks}</dd>
            </div>
          )}
        </dl>

        {claim.status === "approved" && (
          <div className="mt-6 rounded-xl bg-green-50 p-4">
            <p className="text-sm text-green-800">
              Your claim was approved. Show this QR code at the collection desk.
            </p>
            <button onClick={showQr} className="mt-3 rounded-lg bg-green-600 px-4 py-2 text-sm text-white">
              Show handover QR
            </button>
          </div>
        )}
      </div>

      {claim.status === "pending" && (
        <form onSubmit={handleEvidence} className="mt-6 space-y-4 rounded-2xl border bg-white p-6">
          <h2 className="text-lg font-bold">Additional ownership evidence</h2>

          <select
            value={proofType}
            onChange={(e) => setProofType(e.target.value)}
            className="w-full rounded-lg border px-4 py-3"
          >
            {PROOF_TYPES.map((type) => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          <textarea
            value={proofDetails}
            onChange={(e) => setProofDetails(e.target.value)}
            rows={4}
            maxLength={2000}
            required
            placeholder="Describe the proof (serial number, marks, purchase details...)"
            className="w-full rounded-lg border px-4 py-3"
          />

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-primary px-5 py-3 font-semibold text-white disabled:opacity-60"
          >
            {saving ? "Saving..." : "Submit evidence"}
          </button>
        </form>
      )}
    </main>
  );
}
