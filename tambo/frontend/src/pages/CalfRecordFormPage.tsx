import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type { CalfRecord } from "../api/types";
import { CalfRecordForm } from "../components/CalfRecordForm";

interface CalfRecordFormPageProps {
  mode: "create" | "edit";
}

export function CalfRecordFormPage({ mode }: CalfRecordFormPageProps) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState<CalfRecord | null>(null);
  const [loading, setLoading] = useState(mode === "edit");

  useEffect(() => {
    if (mode === "edit" && id) {
      apiClient.get<CalfRecord>(`/calf-records/${id}`).then((res) => {
        setRecord(res.data);
        setLoading(false);
      });
    }
  }, [mode, id]);

  if (loading) {
    return <p>Cargando...</p>;
  }

  return (
    <div>
      <h2>{mode === "create" ? "Cargar nuevo ternero" : `Editar ternero #${id}`}</h2>
      <CalfRecordForm
        recordId={record?.id}
        initial={record ?? undefined}
        onSaved={() => {
          if (mode === "create") {
            navigate("/");
          }
        }}
      />
    </div>
  );
}
