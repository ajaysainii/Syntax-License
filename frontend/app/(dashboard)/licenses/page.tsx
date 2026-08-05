import { AuthGuard } from "@/app/components/AuthGuard";
import { ResourcePage } from "@/app/components/ResourcePage";

export default function LicensesPage() {
  return (
    <AuthGuard>
      <ResourcePage kind="licenses" />
    </AuthGuard>
  );
}

