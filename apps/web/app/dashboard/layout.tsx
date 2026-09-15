import AuthGuard from "@/components/AuthGuard";
import Nav from "@/components/Nav";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div style={{ display: "flex" }}>
        <Nav />
        <main style={{ flex: 1, padding: "24px 32px", maxWidth: 1100 }}>{children}</main>
      </div>
    </AuthGuard>
  );
}
