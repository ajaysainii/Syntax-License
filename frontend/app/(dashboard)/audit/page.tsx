import { AuthGuard } from "@/app/components/AuthGuard";
import { ResourcePage } from "@/app/components/ResourcePage";

export default function AuditPage() {
  return (
    <AuthGuard>
      <ResourcePage kind="audit" />
    </AuthGuard>
  );
}

