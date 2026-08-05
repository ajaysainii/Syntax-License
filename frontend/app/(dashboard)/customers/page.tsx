import { AuthGuard } from "@/app/components/AuthGuard";
import { ResourcePage } from "@/app/components/ResourcePage";

export default function CustomersPage() {
  return (
    <AuthGuard>
      <ResourcePage kind="customers" />
    </AuthGuard>
  );
}

