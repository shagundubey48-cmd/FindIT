
import { Routes, Route } from "react-router-dom";

function Home() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="flex items-center justify-between px-8 py-5 bg-white shadow-sm">
        <h1 className="text-2xl font-bold text-primary">
          FindIT.
        </h1>

        <div className="flex gap-6 items-center">
          <a href="#home" className="hover:text-primary">Home</a>
          <a href="#about" className="hover:text-primary">About</a>
          <a href="/login" className="hover:text-primary">Login</a>
          <a href="/register" className="bg-primary text-white px-5 py-2 rounded-lg">
            Get Started
          </a>
        </div>
      </nav>

      <section id="home" className="max-w-6xl mx-auto px-6 py-24 text-center">
        <p className="text-primary font-semibold mb-4">
          AI POWERED CAMPUS LOST & FOUND
        </p>

        <h2 className="text-5xl font-bold text-dark leading-tight">
          Lost Something?
          <br />
          <span className="text-primary">Let's Find It Together.</span>
        </h2>

        <p className="text-gray-500 mt-6 max-w-2xl mx-auto">
          FindIT helps students report lost and found belongings
          and intelligently match items using AI.
        </p>

        <div className="flex justify-center gap-4 mt-8">
          <a href="/report-lost" className="bg-primary text-white px-7 py-3 rounded-xl">
            Report Lost Item
          </a>

          <a href="/found-items" className="border border-primary text-primary px-7 py-3 rounded-xl">
            Explore Found Items
          </a>
        </div>
      </section>

      <section id="about" className="bg-white py-16 px-6">
        <h2 className="text-3xl font-bold text-center mb-10">
          How FindIT Works
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            ["01", "Report an Item", "Report your lost or found belongings."],
            ["02", "AI Matching", "Find similar items through intelligent matching."],
            ["03", "Get It Back", "Verify ownership and arrange a handover."]
          ].map(([number, title, description]) => (
            <div key={number} className="p-8 rounded-2xl bg-background">
              <span className="text-primary text-3xl font-bold">{number}</span>
              <h3 className="text-xl font-bold mt-4">{title}</h3>
              <p className="text-gray-500 mt-2">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="text-center py-8 text-gray-500">
        © 2026 FindIT. Campus Lost & Found Platform.
      </footer>
    </div>
  );
}

function Placeholder({ title }) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <h1 className="text-3xl font-bold">{title}</h1>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Placeholder title="Login" />} />
      <Route path="/register" element={<Placeholder title="Register" />} />
      <Route path="/report-lost" element={<Placeholder title="Report Lost Item" />} />
      <Route path="/found-items" element={<Placeholder title="Found Items" />} />
      <Route path="*" element={<Placeholder title="404 - Page Not Found" />} />
    </Routes>
  );
}

