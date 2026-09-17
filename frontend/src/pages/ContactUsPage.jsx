import React, { useState } from 'react';
import { Mail, Phone, Send, CheckCircle2, ExternalLink } from 'lucide-react';
import BlockRevealImage from '../components/BlockRevealImage';

// Authentic Indian Field Photography
import indianExcavatorFacility from '../assets/indian_mines/excavator-terrace-bench.jpg';

export default function ContactUsPage() {
  const [formData, setFormData] = useState({
    name: '',
    organization: '',
    email: '',
    subject: 'telemetry_access',
    priority: 'standard',
    message: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [ticketId, setTicketId] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) return;

    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      setSubmitted(true);
      setTicketId(`MOIL-BLG-${Math.floor(100000 + Math.random() * 900000)}`);
    }, 800);
  };

  return (
    <div className="space-y-14 pb-20 max-w-7xl mx-auto px-4 sm:px-6 pt-6">
      {/* 1. Header */}
      <div className="border-b border-[#DCD5CD] pb-6">
        <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-semibold mb-2 flex items-center gap-2 text-slide-down">
          <Mail className="w-3.5 h-3.5 text-[#C87A5B]" />
          <span>TECHNICAL AND OPERATIONAL INQUIRY</span>
        </div>
        <h1 className="font-editorial text-3xl sm:text-5xl text-[#26211F] font-bold tracking-tight text-slide-down-d1">
          Connect with the Field Operations and Technical Directorate
        </h1>
        <p className="mt-4 font-sans text-base sm:text-lg text-[#5A524F] max-w-3xl leading-relaxed text-slide-down-d2">
          Whether you are an operational engineer requesting real-time telemetry access, an academic researcher examining backtest models, or an industry partner inquiring about ore allocations, our direct communication channels bridge the underground face to the surface.
        </p>
      </div>

      {/* 2. Interactive Transmission & Inquiry Form */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-7 bg-white border border-[#DCD5CD] p-6 sm:p-8 rounded-xl shadow-sm">
          <div className="mb-6">
            <span className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-semibold">
              DISPATCH TRANSMISSION
            </span>
            <h3 className="font-sans text-2xl text-[#26211F] font-bold mt-1">
              Submit Operational Inquiry or Telemetry Request
            </h3>
            <p className="text-xs text-[#5A524F] font-sans mt-1">
              Inquiries are routed immediately to the Surface Dispatch or Technical Engineering Cell.
            </p>
          </div>

          {submitted ? (
            <div className="p-6 bg-emerald-50 border border-emerald-300 rounded-xl text-center space-y-3">
              <CheckCircle2 className="w-10 h-10 text-emerald-700 mx-auto" />
              <h4 className="font-sans text-xl font-bold text-[#26211F]">
                Transmission Successfully Dispatched
              </h4>
              <p className="text-xs font-sans text-[#5A524F]">
                Assigned Reference ID: <span className="text-[#C87A5B] font-bold">{ticketId}</span>
              </p>
              <p className="text-xs text-[#5A524F] max-w-md mx-auto font-sans">
                Our shift telemetry controller will review your submission and contact you at {formData.email} within 2 to 4 business hours.
              </p>
              <button
                onClick={() => {
                  setSubmitted(false);
                  setFormData({
                    name: '',
                    organization: '',
                    email: '',
                    subject: 'telemetry_access',
                    priority: 'standard',
                    message: '',
                  });
                }}
                className="mt-4 px-4 py-2 rounded-lg bg-white border border-[#DCD5CD] text-xs font-sans text-[#5A524F] hover:text-[#26211F] hover:bg-[#EEE6DD] cursor-pointer shadow-sm"
              >
                Send Another Transmission
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 font-sans text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[#26211F] font-medium block">
                    Full Name <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="e.g. S. K. Mukherjee"
                    className="w-full px-3 py-2 bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg text-[#26211F] focus:outline-none focus:border-[#C87A5B] focus:bg-white"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[#26211F] font-medium block">
                    Organization / Mine Division
                  </label>
                  <input
                    type="text"
                    name="organization"
                    value={formData.organization}
                    onChange={handleChange}
                    placeholder="e.g. Central Mining Division"
                    className="w-full px-3 py-2 bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg text-[#26211F] focus:outline-none focus:border-[#C87A5B] focus:bg-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[#26211F] font-medium block">
                    Official Email Address <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="officer@organization.gov.in"
                    className="w-full px-3 py-2 bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg text-[#26211F] focus:outline-none focus:border-[#C87A5B] focus:bg-white"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[#26211F] font-medium block">
                    Inquiry Scope
                  </label>
                  <select
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg text-[#26211F] focus:outline-none focus:border-[#C87A5B] focus:bg-white cursor-pointer"
                  >
                    <option value="telemetry_access">Underground Stope Telemetry Access</option>
                    <option value="backtest_audit">Historical Backtest Data Verification</option>
                    <option value="model_integration">RESTful API Engine Integration</option>
                    <option value="field_visit">Technical Reconnaissance Inquiries</option>
                    <option value="other">General Operational Communication</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[#26211F] font-medium block">
                  Priority Status
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'standard', label: 'Standard (Routine)', color: 'text-[#5A524F]' },
                    { id: 'urgent', label: 'Operational Priority', color: 'text-[#C87A5B] font-semibold' },
                    { id: 'emergency', label: 'Critical / Shortfall Alert', color: 'text-rose-700 font-semibold' },
                  ].map((p) => (
                    <label
                      key={p.id}
                      className={`flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer transition-all ${
                        formData.priority === p.id
                          ? 'bg-[#EDC7B7]/40 border-[#C87A5B] text-[#26211F] font-semibold shadow-sm'
                          : 'bg-[#FAF7F2] border-[#DCD5CD] text-[#5A524F] hover:text-[#26211F]'
                      }`}
                    >
                      <input
                        type="radio"
                        name="priority"
                        value={p.id}
                        checked={formData.priority === p.id}
                        onChange={handleChange}
                        className="accent-[#C87A5B]"
                      />
                      <span className={`text-[11px] ${p.color}`}>{p.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[#26211F] font-medium block">
                  Detailed Operational Query <span className="text-rose-600">*</span>
                </label>
                <textarea
                  name="message"
                  required
                  rows={4}
                  value={formData.message}
                  onChange={handleChange}
                  placeholder="Specify mine block, equipment telemetry parameters, or statutory reconciliation requirements..."
                  className="w-full px-3 py-2 bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg text-[#26211F] focus:outline-none focus:border-[#C87A5B] focus:bg-white"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 bg-[#C87A5B] hover:bg-[#B85D3B] text-white font-bold text-xs uppercase tracking-wider rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50 shadow-sm"
              >
                {submitting ? (
                  <span>Dispatching Telemetric Packet...</span>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>Transmit Encrypted Query to Control Room</span>
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Right Info Box: Direct Telemetry Access */}
        <div className="lg:col-span-5 space-y-6">
          <BlockRevealImage
            src={indianExcavatorFacility}
            alt="Central India Mining Facility and Terrace Extraction Operations"
            aspectRatio="aspect-[16/10]"
            blockColor="bg-[#C87A5B]"
          />

          <div className="bg-white border border-[#DCD5CD] p-6 border-l-4 border-l-[#C87A5B] rounded-xl shadow-sm space-y-3">
            <h4 className="font-sans text-lg text-[#26211F] font-bold">
              Direct RESTful API Access
            </h4>
            <p className="text-xs text-[#5A524F] leading-relaxed font-sans">
              All spatial rasters, quantile forecast distributions, and historical walk-forward holdouts are available via programmatic REST endpoints for integrated enterprise dispatch systems.
            </p>

            <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD] font-sans text-xs space-y-1.5 text-[#5A524F]">
              <div className="text-[#C87A5B] font-bold font-mono"># Live Endpoint Examples:</div>
              <div className="font-mono">GET /api/forecast/production</div>
              <div className="font-mono">GET /api/historical/backtest</div>
              <div className="font-mono">GET /api/prospectivity/map</div>
              <div className="font-mono">POST /api/simulate/scenario</div>
            </div>

            <div className="pt-2">
              <a
                href="/docs"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-sans text-[#C87A5B] font-semibold hover:underline"
              >
                <span>View Complete OpenAPI Specification</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="bg-white border border-[#DCD5CD] p-6 rounded-xl shadow-sm space-y-2">
            <h4 className="font-sans text-lg text-[#26211F] font-bold">
              Emergency Surface Dispatch
            </h4>
            <p className="text-xs text-[#5A524F] font-sans leading-relaxed">
              In case of stope geological instabilities or critical equipment failure during an active underground cycle, bypass the digital form and contact the shaft control room directly.
            </p>
            <div className="pt-2 flex items-center gap-2 text-rose-700 font-sans text-xs font-bold">
              <Phone className="w-3.5 h-3.5" />
              <span>Emergency Dispatch Hotline: +91 7632 245 999</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
