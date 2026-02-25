import { api } from "@/lib/api";
import { useState } from "react";
import Layout from "@/components/dashboard/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload } from "lucide-react";

function UploadBox({ title, endpoint }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  async function onUpload() {
    if (!file) {
      setStatus("Please select a file to upload.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    await api.post(endpoint, formData(), {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    setStatus("File uploaded successfully.");
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <div className="flex items-center gap-3">
          <Button onClick={onUpload} disabled={!file}>
            <Upload className="mr-2 h-4 w-4" />
            Last opp
          </Button>
          <div className="text-sm text-muted-foreground">{status}</div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function UploadPage() {
  return (
    <Layout title="Importer data">
      <div className="grid gap-4 md:grid-cols-2">
        <UploadBox
          title="Transaksjoner (CSV)"
          endpoint="/upload/nordnet/transactions"
        />
        <UploadBox
          title="Beholdning (CSV)"
          endpoint="/upload/nordnet/holdings"
        />
      </div>

      <div className="mt-6 text-sm text-muted-foreground">
        Tips: Transaksjoner gir historikken. Beholdning er “fasit nå” og hjelper
        når CSV/korporate actions er rare.
      </div>
    </Layout>
  );
}
