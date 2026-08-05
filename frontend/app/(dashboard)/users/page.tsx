import { AuthGuard } from "@/app/components/AuthGuard";
import { ResourcePage } from "@/app/components/ResourcePage";

export default function UsersPage() {
  return (
    <AuthGuard>
      <ResourcePage kind="users" />
    </AuthGuard>
  );
}

