#!/bin/bash
# setup.sh - Orleans Postgres Init (curl + indexed order)
# chmod +x setup.sh && ./setup.sh

set -e

echo "🛠️ Downloading Orleans AdoNet Postgres scripts (indexed order)..."

mkdir -p orleans-scripts
cd orleans-scripts

# 01-Main.sql: Core (orleansquery table)
curl -sSL -o 01-PostgreSQL-Main.sql \
  https://raw.githubusercontent.com/dotnet/orleans/main/src/AdoNet/Shared/PostgreSQL-Main.sql

# 02-Clustering.sql: Membership tables
curl -sSL -o 02-PostgreSQL-Clustering.sql \
  https://raw.githubusercontent.com/dotnet/orleans/main/src/AdoNet/Orleans.Clustering.AdoNet/PostgreSQL-Clustering.sql

# 🐛 Fix Orleans PostgreSQL clustering bug: Add missing CleanupDefunctSiloEntriesKey
# https://github.com/dotnet/orleans/issues/8216 & PR #9125
cat >> 02-PostgreSQL-Clustering.sql << 'EOF'

-- Fix: Missing CleanupDefunctSiloEntriesKey query (Orleans 7+ runtime requires it)
INSERT INTO OrleansQuery(QueryKey, QueryText)
VALUES
(
    'CleanupDefunctSiloEntriesKey','
    DELETE FROM OrleansMembershipTable
    WHERE DeploymentId = @DeploymentId
        AND @DeploymentId IS NOT NULL
        AND IAmAliveTime < @IAmAliveTime
        AND Status != 3;
');
EOF

echo "✅ Added missing CleanupDefunctSiloEntriesKey to 02-PostgreSQL-Clustering.sql"


# 03-Persistence.sql: Grain state (your "urls")
curl -sSL -o 03-PostgreSQL-Persistence.sql \
  https://raw.githubusercontent.com/dotnet/orleans/main/src/AdoNet/Orleans.Persistence.AdoNet/PostgreSQL-Persistence.sql

# 04-Reminders.sql: Optional (grain timers)
curl -sSL -o 04-PostgreSQL-Reminders.sql \
  https://raw.githubusercontent.com/dotnet/orleans/main/src/AdoNet/Orleans.Reminders.AdoNet/PostgreSQL-Reminders.sql

chmod 644 0*-*.sql

echo "✅ Scripts (indexed run order):"
ls -la 0*-*.sql
echo ""
echo "🚀 -> running : docker-compose up -d  # Runs 01→04 auto"
docker-compose up -d
echo "⏳ Waiting 3s for PostgreSQL to initialize and run init scripts..."
sleep 3

echo "🔄 Reset dev: docker-compose down -v && docker-compose up -d postgres"
echo "📋 -> running : Verify: docker-compose exec postgres psql -U devuser -d orleans -c '\\dt orleans*'"
docker-compose exec postgres psql -U devuser -d orleans -c '\dt orleans*'

echo ""
echo "⚙️ Silo conn string:"
echo 'Host=localhost;Database=orleans;Username=devuser;Password=devpass'
