import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  decideAdminClaim,
  getAdminClaim,
  verifyHandoverQr,
} from "../../services/adminService";
import { confirmHandover } from "../../services/handoverService";
import Loader from "../../components/Loader";
import {
  formatDateTime,
  getErrorMessage,
  statusClasses,
  titleCase,
} from "../../utils/helpers";

export default function ClaimReview() {
  const { id } = useParams();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [remarks, setRemarks] = useState("");
  const [notes, setNotes] = useState("");
  const [qrToken, setQrToken] = useState("");
  const [qrResult, setQrResult] = useState(null);

  const load = useCallback(async () => {
    try {
      const { data } = await getAdminClaim(id);
      setClaim(data.claim);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const run = async (action, successMessage) => {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      setNotice(successMessage);
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const decide = (status) => {
    if (!remarks.trim()) {
      setError("Administrator remarks are required.");
      return;
    }
    run(
      () => decideAdminClaim(id, { status, admin_remarks: remarks.trim() }),
      `Claim ${status}.`
    );
  };

  const handleVerifyQr = async (event) => {
    event.preventDefault();
    setError("");
    setQrResult(null);
    try {
      const { data } = await verifyHandoverQr(qrToken.trim());
      setQrResult(data);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  if (loading) return <Loader />;

  if (!claim) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-10">
        <p className="rounded bg-red-50 p-3 text-red-700">{error || "Claim not found."}</p>
        <Link to="/admin/claims" className="mt-4 inline-block text-primary">Back to claims</Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-5 py-10">
      <Link to="/admin/claims" className="text-sm text-primary">← All claims</Link>

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

        {error && <p className="mt-4 rounded bg-red-50 p-3 text-red-700">{error}</p>}
        {notice && <p className="mt-4 rounded bg-green-50 p-3 text-green-700">{notice}</p>}

        <dl className="mt-6 space-y-4 text-sm">
          <div><dt className="font-medium text-slate-500">Claimant</dt><dd>{claim.claimant_name} ({claim.claimant_email})</dd></div>
          <div><dt className="font-medium text-slate-500">Ownership details</dt><dd className="whitespace-pre-wrap">{claim.ownership_details}</dd></div>
          <div>
            <dt className="font-medium text-slate-500">Proof</dt>
            <dd>{claim.proof_type ? `${titleCase(claim.proof_type)}: ${claim.proof_details}` : "No additional evidence submitted."}</dd>
          </div>
          <div><dt className="font-medium text-slate-500">Last updated</dt><dd>{formatDateTime(claim.status_updated_at)}</dd></div>
          {claim.admin_remarks && (
            <div><dt className="font-medium text-slate-500">Remarks</dt><dd>{claim.admin_remarks}</dd></div>
          )}
        </dl>

        {claim.status === "pending" && (
          <div className="mt-6 space-y-3 border-t pt-5">
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              rows={3}
              maxLength={2000}
              placeholder="Administrator remarks (required)"
              className="w-full rounded-lg border p-3"
            />
            <div className="flex gap-3">
              <button disabled={busy} onClick={() => decide("approved")} className="rounded-lg bg-green-600 px-5 py-2 text-white disabled:opacity-60">Approve</button>
              <button disabled={busy} onClick={() => decide("rejected")} className="rounded-lg bg-red-600 px-5 py-2 text-white disabled:opacity-60">Reject</button>
            </div>
          </div>
        )}

        {claim.status === "approved" && (
          <div className="mt-6 space-y-4 border-t pt-5">
            <form onSubmit={handleVerifyQr} className="space-y-2">
              <h2 className="font-bold">Verify claimant's QR code</h2>
              <input
                value={qrToken}
                onChange={(e) => setQrToken(e.target.value)}
                required
                placeholder="Paste the scanned QR token"
                className="w-full rounded-lg border px-3 py-2"
              />
              <button className="rounded-lg border px-4 py-2 text-sm">Verify</button>
              {qrResult?.valid && (
                <p className="text-sm text-green-700">
                  Valid: claim #{qrResult.claim_id} for "{qrResult.item_title}" ({qrResult.claimant_name})
                </p>
              )}
            </form>

            <div className="space-y-2">
              <h2 className="font-bold">Record handover</h2>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                maxLength={2000}
                placeholder="Handover notes (optional)"
                className="w-full rounded-lg border p-3"
              />
              <button
                disabled={busy}
                onClick={() => run(() => confirmHandover(id, { handover_notes: notes }), "Handover recorded.")}
                className="rounded-lg bg-primary px-5 py-2 text-white disabled:opacity-60"
              >
                Confirm handover
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
