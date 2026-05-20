// Ishak: 3 блоки — фонд команди, твій баланс, останні транзакції
import React from 'react';

const Dashboard = ({fund, balance}) => {
    return (
        <div className="flex flex-col gap-4">

            <div className="bg-gray-100 p-5 rounded-2xl shadow-sm">
                <h2 className="text-gray-500 text-sm font-medium">Загальний фонд команди</h2>

                <p className = "text-3xl font-bold mt-1">${fund}</p>
            </div>
        


            <div className = "bg-blue-50 p-5 rounded-2xl shadow-sm border border-blue-100">
                <h2 className = "text-blue-500 text-sm font-medium">Мій доступний баланс</h2>
                <p className = "text-3xl font-bold mt-1 text-vlue-700">${balance}</p>
            </div>

        </div>
    );
};

export default Dashboard;




