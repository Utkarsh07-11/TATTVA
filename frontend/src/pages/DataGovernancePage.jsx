import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Building2,
  Users,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Download,
  PlusCircle,
  RefreshCw,
  Search,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function DataGovernancePage() {
  const { user, token, tier, setIsCommissionModalOpen, setIsWeeklyModalOpen } = useAuth();

  const [matrixData, setMatrixData] = useState(null);
  const [auditData, setAuditData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [rosterFile, setRosterFile] = useState(null);
  const [rosterStatus, setRosterStatus] = useState(null);
  const [rosterLoading, setRosterLoading] = useState(false);

  const fetchGovernanceData = async () => {
    setLoading(true);
    try {
      const [matRes, audRes] = await Promise.all([
        fetch('/api/governance/compliance-matrix'),
        fetch('/api/governance/audit-trail?limit=25'),
      ]);

      if (matRes.ok) {
        const d = await matRes.json();
        setMatrixData(d);
      }
      if (audRes.ok) {
        const a = await audRes.json();
        setAuditData(a.audit_trail || []);
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGovernanceData();
  }, []);

  const handleDownloadRosterTemplate = async () => {
    try {
      const res = await fetch('/api/governance/sample-csv/employee-roster');
      const text = await res.text();
      const blob = new Blob([text], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'moil_sample_employee_roster.csv';
      a.click();
    } catch {
      // fallback
    }
  };

  const handleUploadRoster = async (e) => {
    e.preventDefault();
    if (!rosterFile) return;
    setRosterLoading(true);
    setRosterStatus(null);
    try {
      const formData = new FormData();
      formData.append('file', rosterFile);
      const res = await fetch('/api/governance/onboard-roster', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Roster onboarding failed');
      setRosterStatus({ success: true, message: data.message });
      setRosterFile(null);
      fetchGovernanceData();
    } catch (err) {
      setRosterStatus({ success: false, message: err.message });
    } finally {
      setRosterLoading(false);
    }
  };

  const filteredMines = (matrixData?.matrix || []).filter((m) =>
    m.mine_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.state.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.mine_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#F7F4EF] text-[#26211F] pb-20">
      {/* Header Banner */}
      <section className="border-b border-[#DCD5CD] bg-[#FAF7F2] py-10">
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-sans font-semibold bg-[#EEE6DD] border border-[#DCD5CD] text-[#5A524F]">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#C87A5B]" />
                  Statutory Oversight &amp; Multi-Mine Governance
                </span>
                <span className="text-xs text-[#8A817D] font-mono">
                  September 2026 Cycle
                </span>
              </div>
              <h1 className="font-editorial text-2xl sm:text-3xl font-bold tracking-tight text-[#26211F]">
                Data Governance &amp; Statutory Compliance
              </h1>
              <p className="font-sans text-xs sm:text-sm text-[#5A524F] max-w-2xl mt-1">
                Authoritative compliance tracking across MOIL statutory leases, weekly operational reconciliation, and workforce credential governance.
              </p>
            </div>

            <div className="flex items-center gap-2.5 shrink-0">
              <button
                type="button"
                onClick={fetchGovernanceData}
                className="p-2 rounded-lg border border-[#DCD5CD] bg-white hover:bg-[#EEE6DD] text-[#5A524F] transition-colors cursor-pointer shadow-sm"
                title="Refresh Matrix"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>

              <button
                type="button"
                onClick={() => setIsWeeklyModalOpen(true)}
                className="px-3.5 py-2 rounded-lg border border-[#B85D3B] bg-[#C87A5B] hover:bg-[#B85D3B] text-white text-xs font-sans font-semibold transition-colors cursor-pointer shadow-sm"
              >
                + Log Weekly WSR
              </button>

              {tier === 3 && (
                <button
                  type="button"
                  onClick={() => setIsCommissionModalOpen(true)}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-purple-300 bg-purple-700 hover:bg-purple-800 text-white text-xs font-sans font-semibold transition-colors cursor-pointer shadow-sm"
                >
                  <PlusCircle className="w-3.5 h-3.5 text-purple-200" />
                  <span>Commission Mine</span>
                </button>
              )}
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 font-sans">
            <div className="p-3.5 rounded-xl bg-white border border-[#DCD5CD] shadow-sm">
              <span className="text-xs text-[#8A817D] block mb-1">Monitored Leases</span>
              <div className="text-2xl font-bold font-mono text-[#26211F]">
                {matrixData?.total_mines || 10}
              </div>
              <span className="text-[11px] text-[#8A817D]">
                10 MOIL Statutory + Commissioned
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-white border border-[#DCD5CD] shadow-sm">
              <span className="text-xs text-[#8A817D] block mb-1">Active Cycle</span>
              <div className="text-xl font-bold font-mono text-[#C87A5B]">
                Week 3 (Active)
              </div>
              <span className="text-[11px] text-[#8A817D]">
                Sep 15 – Sep 21, 2026
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-white border border-[#DCD5CD] shadow-sm">
              <span className="text-xs text-[#8A817D] block mb-1">Total MTD Production</span>
              <div className="text-2xl font-bold font-mono text-emerald-700">
                {((matrixData?.matrix || []).reduce((acc, m) => acc + (m.month_actual_tonnes || 0), 0)).toLocaleString()} t
              </div>
              <span className="text-[11px] text-[#8A817D]">
                Verified via Weekly DSR Logs
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-white border border-[#DCD5CD] shadow-sm">
              <span className="text-xs text-[#8A817D] block mb-1">Current User Role</span>
              <div className="text-lg font-bold font-mono text-[#26211F] truncate">
                {user?.role}
              </div>
              <span className="text-[11px] text-[#8A817D] font-mono">
                {user?.employee_id} · Tier {tier}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-[1440px] mx-auto px-5 sm:px-8 mt-8 space-y-10">
        {/* Section 1: 10-Mine Statutory Compliance Matrix */}
        <section className="border border-[#DCD5CD] rounded-xl bg-white p-5 sm:p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
            <div>
              <h2 className="font-editorial text-lg font-bold tracking-tight text-[#26211F] flex items-center gap-2">
                <Building2 className="w-4 h-4 text-[#C87A5B]" />
                <span>Multi-Mine Statutory Submission Compliance Matrix</span>
              </h2>
              <p className="font-sans text-xs text-[#5A524F]">
                Weekly Operational Summaries (WSR Week 1–4) for September 2026
              </p>
            </div>

            <div className="relative w-full sm:w-64">
              <input
                type="text"
                placeholder="Filter by mine, state, or ID…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs bg-[#FAF7F2] border border-[#DCD5CD] focus:border-[#C87A5B] rounded-lg text-[#26211F] placeholder:text-[#8A817D] font-sans"
              />
              <Search className="w-3.5 h-3.5 text-[#8A817D] absolute left-2.5 top-2.5" />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-sans text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#DCD5CD] text-[11px] text-[#8A817D] uppercase tracking-wider bg-[#FAF7F2]">
                  <th className="py-2.5 px-3">Mine Lease</th>
                  <th className="py-2.5 px-3">State / District</th>
                  <th className="py-2.5 px-3 text-center">Week 1</th>
                  <th className="py-2.5 px-3 text-center">Week 2</th>
                  <th className="py-2.5 px-3 text-center">Week 3 (Due)</th>
                  <th className="py-2.5 px-3 text-center">Week 4</th>
                  <th className="py-2.5 px-3 text-right">MTD Tonnes</th>
                  <th className="py-2.5 px-3 text-right">Compliance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DCD5CD] font-mono">
                {filteredMines.map((m) => (
                  <tr key={m.mine_id} className="hover:bg-[#FAF7F2] transition-colors">
                    <td className="py-3 px-3 font-sans font-semibold text-[#26211F]">
                      <div>{m.mine_name}</div>
                      <div className="text-[10px] text-[#8A817D] font-mono">{m.mine_id}</div>
                    </td>
                    <td className="py-3 px-3 font-sans text-[#5A524F]">
                      {m.district ? `${m.district}, ` : ''}{m.state}
                    </td>

                    {/* Week 1 */}
                    <td className="py-3 px-3 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] border ${
                        m.weeks?.week_1?.status === 'SUBMITTED'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : 'bg-[#EDC7B7]/40 text-[#8C3A1E] border border-[#C87A5B]/40'
                      }`}>
                        {m.weeks?.week_1?.status === 'SUBMITTED' ? `${m.weeks.week_1.actual_tonnes} t` : 'PENDING'}
                      </span>
                    </td>

                    {/* Week 2 */}
                    <td className="py-3 px-3 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] border ${
                        m.weeks?.week_2?.status === 'SUBMITTED'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : 'bg-[#EDC7B7]/40 text-[#8C3A1E] border border-[#C87A5B]/40'
                      }`}>
                        {m.weeks?.week_2?.status === 'SUBMITTED' ? `${m.weeks.week_2.actual_tonnes} t` : 'PENDING'}
                      </span>
                    </td>

                    {/* Week 3 (Current Active) */}
                    <td className="py-3 px-3 text-center">
                      <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] border font-bold ${
                        m.weeks?.week_3?.status === 'SUBMITTED'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : 'bg-[#C87A5B] text-white border-[#B85D3B] shadow-sm animate-pulse'
                      }`}>
                        {m.weeks?.week_3?.status === 'SUBMITTED' ? `${m.weeks.week_3.actual_tonnes} t` : 'DUE NOW'}
                      </span>
                    </td>

                    {/* Week 4 */}
                    <td className="py-3 px-3 text-center">
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] border bg-[#EEE6DD] text-[#8A817D] border-[#DCD5CD]">
                        UPCOMING
                      </span>
                    </td>

                    <td className="py-3 px-3 text-right font-semibold text-[#26211F]">
                      {m.month_actual_tonnes.toLocaleString()} t
                    </td>

                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <span className={`text-xs font-bold ${m.compliance_pct >= 50 ? 'text-emerald-700' : 'text-[#C87A5B]'}`}>
                          {m.compliance_pct}%
                        </span>
                        <div className="w-12 h-1.5 bg-[#EEE6DD] rounded-full overflow-hidden">
                          <div
                            className={`h-full ${m.compliance_pct >= 50 ? 'bg-emerald-600' : 'bg-[#C87A5B]'}`}
                            style={{ width: `${m.compliance_pct}%` }}
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 2: Workforce Roster Bulk Onboarding & Audit Trail */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bulk Onboarding Box */}
          <section className="border border-[#DCD5CD] rounded-xl bg-white p-5 sm:p-6 font-sans shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-[#DCD5CD] pb-3">
              <div>
                <h2 className="font-editorial text-lg font-bold tracking-tight text-[#26211F] flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#C87A5B]" />
                  <span>Bulk Employee Roster Ingestion</span>
                </h2>
                <p className="text-xs text-[#5A524F]">
                  Onboard new mine staff across India without manual code edits
                </p>
              </div>

              <button
                type="button"
                onClick={handleDownloadRosterTemplate}
                className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#FAF7F2] hover:bg-[#EEE6DD] border border-[#DCD5CD] text-[#5A524F] text-xs transition-colors cursor-pointer"
              >
                <Download className="w-3 h-3 text-[#5A524F]" />
                <span>Template CSV</span>
              </button>
            </div>

            <form onSubmit={handleUploadRoster} className="space-y-4 text-xs">
              <div className="border border-dashed border-[#DCD5CD] rounded-xl p-5 text-center bg-[#FAF7F2]">
                <FileSpreadsheet className="w-8 h-8 text-[#C87A5B] mx-auto mb-2" />
                <p className="text-[#5A524F] mb-1">
                  Upload CSV containing employee_id, full_name, role, mine_id
                </p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setRosterFile(e.target.files?.[0] || null)}
                  className="block mx-auto text-xs text-[#5A524F] file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:bg-[#EDC7B7]/50 file:text-[#8C3A1E] cursor-pointer"
                />
                {rosterFile && (
                  <div className="mt-2 text-emerald-700 font-mono font-semibold">
                    Ready: {rosterFile.name}
                  </div>
                )}
              </div>

              {rosterStatus && (
                <div className={`p-2.5 rounded-lg border text-xs flex items-center gap-2 ${
                  rosterStatus.success
                    ? 'bg-emerald-100 border-emerald-300 text-emerald-800'
                    : 'bg-rose-100 border-rose-300 text-rose-800'
                }`}>
                  {rosterStatus.success ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-rose-700 shrink-0" />
                  )}
                  <span>{rosterStatus.message}</span>
                </div>
              )}

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={!rosterFile || rosterLoading}
                  className="px-5 py-2 rounded-lg bg-[#C87A5B] hover:bg-[#B85D3B] text-white font-bold transition-all cursor-pointer disabled:opacity-50 shadow-sm"
                >
                  {rosterLoading ? 'Enrolling Staff…' : 'Enroll Personnel via CSV'}
                </button>
              </div>
            </form>
          </section>

          {/* Statutory Audit Trail */}
          <section className="border border-[#DCD5CD] rounded-xl bg-white p-5 sm:p-6 font-sans shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-[#DCD5CD] pb-3">
              <div>
                <h2 className="font-editorial text-lg font-bold tracking-tight text-[#26211F] flex items-center gap-2">
                  <Clock className="w-4 h-4 text-[#C87A5B]" />
                  <span>Immutable Statutory Audit Trail</span>
                </h2>
                <p className="text-xs text-[#5A524F]">
                  Cryptographic log of all WSR submissions and administration events
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-[#EEE6DD] border border-[#DCD5CD] text-[#5A524F]">
                {auditData.length} records
              </span>
            </div>

            <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
              {auditData.map((item) => (
                <div
                  key={item.id}
                  className="p-2.5 rounded-lg bg-[#FAF7F2] border border-[#DCD5CD] hover:border-[#C87A5B]/50 text-xs transition-colors"
                >
                  <div className="flex items-center justify-between text-[10px] font-mono text-[#8A817D] mb-1">
                    <span className="text-[#C87A5B] font-semibold">{item.event_type}</span>
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="text-[#5A524F] text-[11px] leading-relaxed">
                    {item.details}
                  </p>
                  <div className="text-[10px] text-[#8A817D] font-mono mt-1">
                    Actor: <span className="text-[#26211F] font-semibold">{item.actor_id}</span> · Target: {item.target_entity}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
