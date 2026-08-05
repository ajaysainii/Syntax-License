import { AuthGuard } from "@/app/components/AuthGuard";
import { ResourcePage } from "@/app/components/ResourcePage";

export default function AdminsPage() {
  return (
    <AuthGuard>
      <ResourcePage kind="admins" />
    </AuthGuard>
  );
}
