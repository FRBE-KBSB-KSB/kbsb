# @app.get("/api/excel", include_in_schema=False)
# def api_excel():
#     logger.info(f"calling excel endpoint {ROOT_DIR}")
#     excpath = ROOT_DIR / "src" / "kbsb" / "templates" / "test" / "test.xlsx"
#     with open(excpath, "rb") as f:
#         buf = f.read()
#     headers = {"Content-Disposition": 'attachment; filename="test.xlsx"'}
#     return StreamingResponse(
#         iter([buf]),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers=headers,
#     )
