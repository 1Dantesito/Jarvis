import pytest
from tools.implementations.task_tools import CreateTaskTool, ListTasksTool, ClearTasksTool
from core.memory_manager import memory_manager

@pytest.mark.asyncio
async def test_custom_lists_crud_and_filtering():
    create_tool = CreateTaskTool()
    list_tool = ListTasksTool()
    clear_tool = ClearTasksTool()

    # Limpiar antes
    await clear_tool.execute()

    # 1. Crear tareas en una lista personalizada "Comida Italiana"
    res1 = await create_tool.execute(title="Pizza Napolitana", project="Comida Italiana", description="Con albahaca fresca")
    assert res1["success"] is True
    assert res1["data"]["project"] == "Comida Italiana"

    res2 = await create_tool.execute(title="Risotto ai Funghi", project="Comida Italiana")
    assert res2["success"] is True

    # 2. Crear tarea en otra lista "Compras"
    res3 = await create_tool.execute(title="Comprar leche", project="Compras")
    assert res3["success"] is True

    # 3. Listar solo las tareas de "Comida Italiana"
    list_res = await list_tool.execute(project="comida italiana")
    assert list_res["success"] is True
    tasks_italiana = list_res["data"]["tasks"]
    titles = [t["title"] for t in tasks_italiana]
    assert "Pizza Napolitana" in titles
    assert "Risotto ai Funghi" in titles
    assert "Comprar leche" not in titles

    # 4. Vaciar solo la lista "Comida Italiana"
    clear_res = await clear_tool.execute(project="Comida Italiana")
    assert clear_res["success"] is True

    # 5. Verificar que "Compras" aún existe intacta
    list_compras = await list_tool.execute(project="Compras")
    assert len(list_compras["data"]["tasks"]) == 1
    assert list_compras["data"]["tasks"][0]["title"] == "Comprar leche"

    # Limpieza final
    await clear_tool.execute()
