import Layout from "@/components/dashboard/Layout";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <Layout
      title="Oversikt"
      right={
        <Button
          variant="secondary"
          onClick={() => (window.location.href = "/upload")}
        >
          Importer
        </Button>
      }
    >
      <div className="text-muted-foreground">
        Neste: KPI-kort, holdings-tabell, og graf.
      </div>
    </Layout>
  );
}
