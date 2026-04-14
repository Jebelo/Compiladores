program PruebaLexer;

{ Declaración de variables }
var
 // 2edad : Integer; ejemplo que tiene que dar error ya que un ID no puede ser primero con numero
  precio : Real;
  contador, total : Integer;
  nombre : String;
  activo : Boolean;

(* Inicio del programa *)
begin

  edad := 25;
  precio := 19.99;
  contador := 0;
  total := 10;

  // ciclo while
  while contador < total do
  begin
    contador := contador + 1;
  end;

  // condicional
  if edad >= 18 then
  begin
    activo := 1;
  end
  else
  begin
    activo := 0;
  end;

  // ciclo for
  for contador := 1 to 5 do
  begin
    total := total + contador;
  end;

  // repeat until
  repeat
    contador := contador - 1;
  until contador = 0;

end.