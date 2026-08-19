-- Asset Maintenance & Inventory Analytics
SELECT Status, COUNT(*) AS Record_Count FROM asset_maintenance GROUP BY Status;
SELECT ROUND(SUM(COALESCE(Maintenance_Cost_INR,0)),2) AS Total_Maintenance_Cost_INR FROM asset_maintenance;
SELECT Location, ROUND(SUM(COALESCE(Maintenance_Cost_INR,0)),2) AS Maintenance_Cost_INR,
SUM(Maintenance_Days) AS Maintenance_Days FROM asset_maintenance GROUP BY Location ORDER BY Maintenance_Cost_INR DESC;
SELECT Asset_Type, COUNT(*) AS Records,
SUM(CASE WHEN Status='Under Maintenance' THEN 1 ELSE 0 END) AS Under_Maintenance,
SUM(Maintenance_Days) AS Maintenance_Days,
ROUND(SUM(COALESCE(Maintenance_Cost_INR,0)),2) AS Maintenance_Cost_INR
FROM asset_maintenance GROUP BY Asset_Type ORDER BY Maintenance_Cost_INR DESC;
SELECT Inventory_Item, Inventory_Stock, Reorder_Level, Stock_Status
FROM asset_maintenance WHERE Stock_Status='Low Stock';
SELECT strftime('%Y-%m',Maintenance_Date) AS Month,
ROUND(SUM(COALESCE(Maintenance_Cost_INR,0)),2) AS Maintenance_Cost_INR
FROM asset_maintenance GROUP BY Month ORDER BY Month;
